import cv2
import mediapipe as mp
from core.utils import ponto_em_pixels, redimensionar, calcular_angulo
import core.config as config

mp_pose = mp.solutions.pose

# ========================================
# 🎛️ CONFIGURAÇÕES DO SISTEMA
# ========================================

TOLERANCIA_QUADRIL = config.TOLERANCIA_QUADRIL_DEADLIFT
MIN_SUBIDA_OMBRO = config.MIN_SUBIDA_OMBRO_DEADLIFT
FRAMES_ANALISE = config.FRAMES_ANALISE_DEADLIFT
MAX_WIDTH = config.MAX_WIDTH
MAX_HEIGHT = config.MAX_HEIGHT

# ========================================
# INÍCIO DO CÓDIGO
# ========================================

def analisar_deadlift(cap):
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils

    min_hip_y = {"direito": None, "esquerdo": None}
    modo_analise = {"direito": False, "esquerdo": False}
    buffer_subida = {"direito": [], "esquerdo": []}
    contador_frames = {"direito": 0, "esquerdo": 0}
    feedback_subida_geral = ""
    subida_resultado = {"direito": None, "esquerdo": None}
    trajetoria_barra = []  # Novo: para desenhar linha da barra
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
                    "direito": (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_SHOULDER,
                                mp_pose.PoseLandmark.RIGHT_WRIST),
                    "esquerdo": (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_SHOULDER,
                                 mp_pose.PoseLandmark.LEFT_WRIST)
                }

                wrist_xs = []
                wrist_ys = []

                for lado, (hip_id, shoulder_id, wrist_id) in lados.items():
                    hip_x, hip_y = ponto_em_pixels(landmarks[hip_id], w, h)
                    shoulder_x, shoulder_y = ponto_em_pixels(landmarks[shoulder_id], w, h)
                    wrist_x, wrist_y = ponto_em_pixels(landmarks[wrist_id], w, h)

                    wrist_xs.append(wrist_x)
                    wrist_ys.append(wrist_y)

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

                # Estimar posição da barra e salvar trajetória
                if wrist_xs and wrist_ys:
                    barra_x = int(sum(wrist_xs) / len(wrist_xs))
                    offset_pixels = 27  # ou 20, teste o que encaixa melhor
                    barra_y = int(sum(wrist_ys) / len(wrist_ys)) + offset_pixels
                    trajetoria_barra.append((barra_x, barra_y))
                    cv2.circle(frame, (barra_x, barra_y), 8, (255, 255, 0), -1)  # Círculo para visualização
                    print(f"🔧 Posição estimada da barra: ({barra_x}, {barra_y})")
                else:
                    print("⚠️ Punhos não detectados neste frame.")

                if all(resultado is not None for resultado in subida_resultado.values()):
                    if all(resultado == "coordenada" for resultado in subida_resultado.values()):
                        feedback_subida_geral = "Subida coordenada"
                    else:
                        feedback_subida_geral = "Subida desequilibrada"
                    subida_resultado = {"direito": None, "esquerdo": None}

            if frame is not None:
                frame_show = redimensionar(frame, MAX_WIDTH, MAX_HEIGHT)

                # Desenhar trajetória da barra com tolerância
                if len(trajetoria_barra) > 1:
                    x_inicial = trajetoria_barra[0][0]
                    x_final = trajetoria_barra[-1][0]
                    desvio_lateral = abs(x_final - x_inicial)
                    tolerancia = 20  # pixels
                    cor = (0, 255, 0) if desvio_lateral <= tolerancia else (0, 0, 255)
                    for i in range(1, len(trajetoria_barra)):
                        cv2.line(frame_show, trajetoria_barra[i-1], trajetoria_barra[i], cor, 2)

                y_offset = 40
                if feedback_subida_geral:
                    cor = (0, 255, 0) if "✅" in feedback_subida_geral else (0, 0, 255)
                    cv2.putText(frame_show, feedback_subida_geral, (20, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2)

                cv2.imshow("Análise Deadlift", frame_show)

            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
