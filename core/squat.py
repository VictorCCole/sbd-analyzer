import cv2
import mediapipe as mp
import math
from core.utils import ponto_em_pixels, redimensionar
import core.config as config

mp_pose = mp.solutions.pose

# ========================================
# 🎛️ CONFIGURAÇÕES DO SISTEMA
# ========================================

ANGULO_MINIMO_PROFUNDIDADE = config.ANGULO_MINIMO_PROFUNDIDADE_SQUAT
TOLERANCIA_QUADRIL = config.TOLERANCIA_QUADRIL_SQUAT
MIN_SUBIDA_OMBRO = config.MIN_SUBIDA_OMBRO_SQUAT
FRAMES_ANALISE = config.FRAMES_ANALISE_SQUAT
MAX_WIDTH = config.MAX_WIDTH
MAX_HEIGHT = config.MAX_HEIGHT

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def calcular_angulo(a, b, c):
    """Calcula o ângulo entre três pontos."""
    angulo = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

# ========================================
# INÍCIO DO CÓDIGO
# ========================================

def analisar_squat(cap):
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils

    # Estado
    min_hip_y = {"direito": None, "esquerdo": None}
    modo_analise = {"direito": False, "esquerdo": False}
    buffer_subida = {"direito": [], "esquerdo": []}
    contador_frames = {"direito": 0, "esquerdo": 0}
    profundidade_status = {"direito": False, "esquerdo": False}
    feedback_subida_geral = ""
    feedback_profundidade_geral = ""
    profundidade_alcancada = False  # <- NOVO: flag para saber se já atingiu profundidade
    subida_resultado = {"direito": None, "esquerdo": None}
    paused = False
    frame = None

    while True:
        if not paused or frame is None:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Fim do vídeo ou erro na leitura.")
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                h, w, _ = frame.shape
                landmarks = results.pose_landmarks.landmark

                mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                lados = {
                    "direito": (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.RIGHT_SHOULDER),
                    "esquerdo": (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.LEFT_SHOULDER)
                }

                for lado, (hip_id, knee_id, ankle_id, shoulder_id) in lados.items():
                    hip_x, hip_y = ponto_em_pixels(landmarks[hip_id], w, h)
                    knee_x, knee_y = ponto_em_pixels(landmarks[knee_id], w, h)
                    ankle_x, ankle_y = ponto_em_pixels(landmarks[ankle_id], w, h)
                    shoulder_x, shoulder_y = ponto_em_pixels(landmarks[shoulder_id], w, h)

                    # Analisar profundidade
                    if not profundidade_alcancada:
                        angulo_joelho = calcular_angulo((hip_x, hip_y), (knee_x, knee_y), (ankle_x, ankle_y))
                        profundidade_status[lado] = angulo_joelho < ANGULO_MINIMO_PROFUNDIDADE

                    # Sempre analisar subida
                    if not modo_analise[lado]:
                        if min_hip_y[lado] is None or hip_y > min_hip_y[lado]:
                            min_hip_y[lado] = hip_y
                        elif hip_y < min_hip_y[lado] - 5:
                            modo_analise[lado] = True
                            buffer_subida[lado] = []
                            contador_frames[lado] = 0
                    else:
                        buffer_subida[lado].append((hip_y, shoulder_y))
                        contador_frames[lado] += 1

                        if contador_frames[lado] >= FRAMES_ANALISE:
                            modo_analise[lado] = False
                            min_hip_y[lado] = None

                            delta_hip = buffer_subida[lado][0][0] - buffer_subida[lado][-1][0]
                            delta_shoulder = buffer_subida[lado][0][1] - buffer_subida[lado][-1][1]

                            if delta_shoulder < MIN_SUBIDA_OMBRO or delta_hip > delta_shoulder + TOLERANCIA_QUADRIL:
                                subida_resultado[lado] = "desequilibrada"
                            else:
                                subida_resultado[lado] = "coordenada"

                # Avaliação geral da profundidade
                if not profundidade_alcancada:
                    if any(profundidade_status.values()):
                        feedback_profundidade_geral = "Profundidade aceitavel"
                        profundidade_alcancada = True
                    else:
                        feedback_profundidade_geral = "Profundidade insuficiente"

                # Avaliação geral da subida
                if all(resultado is not None for resultado in subida_resultado.values()):
                    if all(resultado == "coordenada" for resultado in subida_resultado.values()):
                        feedback_subida_geral = "Subida coordenada"
                    else:
                        feedback_subida_geral = "Subida desequilibrada"
                    subida_resultado = {"direito": None, "esquerdo": None}

            if frame is not None:
                frame_show = redimensionar(frame, MAX_WIDTH, MAX_HEIGHT)

                y_offset = 40
                # Mostrar profundidade geral (fixa depois que atingiu)
                if feedback_profundidade_geral:
                    cor = (0, 255, 0) if "✅" in feedback_profundidade_geral else (0, 0, 255)
                    cv2.putText(frame_show, feedback_profundidade_geral, (20, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2)
                    y_offset += 40

                # Mostrar subida geral
                if feedback_subida_geral:
                    cor = (0, 255, 0) if "✅" in feedback_subida_geral else (0, 0, 255)
                    cv2.putText(frame_show, feedback_subida_geral, (20, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2)

                cv2.imshow("Análise Squat", frame_show)

            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
