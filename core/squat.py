import cv2
import mediapipe as mp
from core.utils import ponto_em_pixels, calcular_angulo
import core.config as config

mp_pose = mp.solutions.pose

TOLERANCIA_QUADRIL = config.TOLERANCIA_QUADRIL_SQUAT
MIN_SUBIDA_OMBRO = config.MIN_SUBIDA_OMBRO_SQUAT
FRAMES_ANALISE = config.FRAMES_ANALISE_SQUAT
ANGULO_MINIMO_PROFUNDIDADE = config.ANGULO_MINIMO_PROFUNDIDADE_SQUAT
ANGULO_MAXIMO_TRONCO = config.ANGULO_MAXIMO_TRONCO

def analisar_squat(cap):
    pose = mp_pose.Pose()
    min_hip_y = {"direito": None, "esquerdo": None}
    modo_analise = {"direito": False, "esquerdo": False}
    buffer_subida = {"direito": [], "esquerdo": []}
    contador_frames = {"direito": 0, "esquerdo": 0}
    profundidade_atingida = {"direito": False, "esquerdo": False}
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

            angulos_tronco = {}

            for lado, (hip_id, knee_id, ankle_id, shoulder_id) in lados.items():
                hip_x, hip_y = ponto_em_pixels(lm[hip_id], w, h)
                knee_x, knee_y = ponto_em_pixels(lm[knee_id], w, h)
                ankle_x, ankle_y = ponto_em_pixels(lm[ankle_id], w, h)
                shoulder_x, shoulder_y = ponto_em_pixels(lm[shoulder_id], w, h)

                # Profundidade via ângulo do joelho
                angulo_joelho = calcular_angulo((hip_x, hip_y), (knee_x, knee_y), (ankle_x, ankle_y))
                profundidade_atingida[lado] = angulo_joelho > ANGULO_MINIMO_PROFUNDIDADE

                # Inclinação do tronco
                angulo_tronco = calcular_angulo((ankle_x, ankle_y), (hip_x, hip_y), (shoulder_x, shoulder_y))
                angulos_tronco[lado] = angulo_tronco

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

        # Profundidade
        if not resultado_profundidade and any(profundidade_atingida.values()):
            resultado_profundidade = "✅ Profundidade adequada – o ângulo do joelho indica amplitude satisfatória."
        elif not resultado_profundidade:
            resultado_profundidade = "❌ Profundidade insuficiente – o joelho não flexionou o suficiente para caracterizar um agachamento válido."

        # Subida coordenada
        if all(subida_resultado.values()) and not resultado_subida:
            if all(r == "coordenada" for r in subida_resultado.values()):
                resultado_subida = "✅ Subida coordenada – quadris e ombros subiram juntos de forma eficiente."
            else:
                resultado_subida = "❌ Subida desequilibrada – os quadris subiram antes dos ombros, indicando falha na coordenação."

        # Postura do tronco (avaliar o lado mais inclinado = menor ângulo)
        if not resultado_tronco and len(angulos_tronco) == 2:
            pior_angulo = min(angulos_tronco.values())
            if pior_angulo < ANGULO_MAXIMO_TRONCO:
                resultado_tronco = "❌ Postura do tronco inadequada – houve inclinação excessiva do tronco durante o movimento."
            else:
                resultado_tronco = "✅ Postura do tronco correta – a inclinação está dentro dos parâmetros técnicos."

    cap.release()

    return [
        resultado_profundidade,
        resultado_subida,
        resultado_tronco
    ]