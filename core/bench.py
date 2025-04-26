import cv2
import mediapipe as mp
import math
from core.utils import ponto_em_pixels, redimensionar

mp_pose = mp.solutions.pose

# ========================================
# 🎛️ CONFIGURAÇÕES DO SISTEMA
# ========================================

MARGEM_PEITO = 15             # Margem em pixels para detectar toque no peito
ANGULO_MINIMO_EXTENSAO = 160  # Ângulo mínimo para considerar extensão completa
MAX_WIDTH = 640
MAX_HEIGHT = 640

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

def analisar_bench(cap):
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils

    tocou_peito = {"direito": False, "esquerdo": False}
    extensao_completa = {"direito": False, "esquerdo": False}
    feedback_geral_peito = ""
    feedback_geral_extensao = ""
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
                    "direito": (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
                    "esquerdo": (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST)
                }

                for lado, (shoulder_id, elbow_id, wrist_id) in lados.items():
                    shoulder_x, shoulder_y = ponto_em_pixels(landmarks[shoulder_id], w, h)
                    elbow_x, elbow_y = ponto_em_pixels(landmarks[elbow_id], w, h)
                    wrist_x, wrist_y = ponto_em_pixels(landmarks[wrist_id], w, h)

                    # Verificar toque no peito
                    if not tocou_peito[lado]:
                        if wrist_y > (shoulder_y + MARGEM_PEITO):
                            tocou_peito[lado] = True

                    # Verificar extensão completa
                    if not extensao_completa[lado]:
                        angulo_cotovelo = calcular_angulo((shoulder_x, shoulder_y), (elbow_x, elbow_y), (wrist_x, wrist_y))
                        if angulo_cotovelo > ANGULO_MINIMO_EXTENSAO:
                            extensao_completa[lado] = True

                # Avaliação geral do toque no peito
                if all(tocou_peito.values()):
                    feedback_geral_peito = "✅ Toque no peito realizado"
                else:
                    feedback_geral_peito = "❌ Toque no peito não detectado"

                # Avaliação geral da extensão
                if all(extensao_completa.values()):
                    feedback_geral_extensao = "✅ Extensão completa"
                else:
                    feedback_geral_extensao = "❌ Extensão incompleta"

            if frame is not None:
                frame_show = redimensionar(frame, MAX_WIDTH, MAX_HEIGHT)

                y_offset = 40
                if feedback_geral_peito:
                    cor = (0, 255, 0) if "✅" in feedback_geral_peito else (0, 0, 255)
                    cv2.putText(frame_show, feedback_geral_peito, (20, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2)
                    y_offset += 40

                if feedback_geral_extensao:
                    cor = (0, 255, 0) if "✅" in feedback_geral_extensao else (0, 0, 255)
                    cv2.putText(frame_show, feedback_geral_extensao, (20, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2)

                cv2.imshow("Análise Bench Press", frame_show)

            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
