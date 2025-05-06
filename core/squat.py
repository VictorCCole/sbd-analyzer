import cv2
import mediapipe as mp
from core.utils import ponto_em_pixels, calcular_angulo
import core.config as config

mp_pose = mp.solutions.pose

TOLERANCIA_QUADRIL = config.TOLERANCIA_QUADRIL_SQUAT
MIN_SUBIDA_OMBRO = config.MIN_SUBIDA_OMBRO_SQUAT
FRAMES_ANALISE = config.FRAMES_ANALISE_SQUAT
ANGULO_MAXIMO_TRONCO = 50  # graus

def analisar_squat(cap):
    pose = mp_pose.Pose()
    min_hip_y = {"direito": None, "esquerdo": None}
    modo_analise = {"direito": False, "esquerdo": False}
    buffer_subida = {"direito": [], "esquerdo": []}
    contador_frames = {"direito": 0, "esquerdo": 0}
    profundidade_status = {"direito": False, "esquerdo": False}
    tronco_status = {"direito": True, "esquerdo": True}
    profundidade_alcancada = False
    subida_resultado = {"direito": None, "esquerdo": None}

    resultado_profundidade = ""
    resultado_subida = ""
    resultado_tronco = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            h, w, _ = frame.shape
            lm = results.pose_landmarks.landmark

            lados = {
                "direito": (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE,
                            mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.RIGHT_SHOULDER),
                "esquerdo": (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE,
                             mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.LEFT_SHOULDER)
            }

            for lado, (hip_id, knee_id, ankle_id, shoulder_id) in lados.items():
                hip_x, hip_y = ponto_em_pixels(lm[hip_id], w, h)
                knee_x, knee_y = ponto_em_pixels(lm[knee_id], w, h)
                ankle_x, ankle_y = ponto_em_pixels(lm[ankle_id], w, h)
                shoulder_x, shoulder_y = ponto_em_pixels(lm[shoulder_id], w, h)

                # Profundidade (uma vez)
                if not profundidade_alcancada and hip_y > knee_y:
                    profundidade_status[lado] = True

                # Inclinação do tronco
                angulo_tronco = calcular_angulo((ankle_x, ankle_y), (hip_x, hip_y), (shoulder_x, shoulder_y))
                tronco_status[lado] = angulo_tronco < ANGULO_MAXIMO_TRONCO

                # Subida coordenada
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

        # Consolidar os feedbacks apenas uma vez
        if not profundidade_alcancada:
            if any(profundidade_status.values()):
                resultado_profundidade = "✅ Profundidade adequada"
            else:
                resultado_profundidade = "❌ Profundidade insuficiente"
            profundidade_alcancada = True

        if all(subida_resultado.values()) and not resultado_subida:
            if all(r == "coordenada" for r in subida_resultado.values()):
                resultado_subida = "✅ Subida coordenada"
            else:
                resultado_subida = "❌ Subida desequilibrada"

        if not resultado_tronco and all(v is not None for v in tronco_status.values()):
            if all(tronco_status.values()):
                resultado_tronco = "✅ Postura do tronco correta"
            else:
                resultado_tronco = "❌ Postura do tronco inadequada"

    cap.release()

    return [
        resultado_profundidade,
        resultado_subida,
        resultado_tronco
    ]