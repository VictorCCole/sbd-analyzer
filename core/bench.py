import cv2
import mediapipe as mp
from core.utils import ponto_em_pixels, calcular_angulo
import core.config as config

mp_pose = mp.solutions.pose

# Configurações
MARGEM_PEITO = config.MARGEM_PEITO_BENCH
ANGULO_MINIMO_EXTENSAO = config.ANGULO_MINIMO_EXTENSAO_BENCH
FRAMES_ANALISE = config.FRAMES_ANALISE_BENCH
TOLERANCIA_MOVIMENTO = config.TOLERANCIA_MOVIMENTO_BENCH
TOLERANCIA_CONTATO = 10  # margem extra para considerar contato válido

def bench(cap):
    pose = mp_pose.Pose(model_complexity=1)
    buffer_movimento = []
    toque_valido = False
    extensao_valida = False

    contatos = {
        "ombros": True,
        "gluteo": True,
        "cabeca": True,
        "pes": True
    }

    frame_inicial = None
    lado_analise = "esquerdo"  # default até sabermos o lado mais visível

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            h, w, _ = frame.shape
            lm = results.pose_landmarks.landmark

            # Coordenadas médias para referência de contato
            ankle_y = (lm[mp_pose.PoseLandmark.LEFT_ANKLE].y + lm[mp_pose.PoseLandmark.RIGHT_ANKLE].y) / 2 * h
            hip_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2 * h
            shoulder_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2 * h
            nose_y = lm[mp_pose.PoseLandmark.NOSE].y * h

            # Detectar lado com maior variação no punho (visível)
            wrist_esq_y = lm[mp_pose.PoseLandmark.LEFT_WRIST].y * h
            wrist_dir_y = lm[mp_pose.PoseLandmark.RIGHT_WRIST].y * h
            lado_analise = "esquerdo" if abs(wrist_esq_y - shoulder_y) > abs(wrist_dir_y - shoulder_y) else "direito"

            barra_y = max(wrist_esq_y, wrist_dir_y)
            buffer_movimento.append(barra_y)
            if len(buffer_movimento) > FRAMES_ANALISE:
                buffer_movimento.pop(0)

            if frame_inicial is None:
                frame_inicial = {
                    "ankle_y": ankle_y,
                    "hip_y": hip_y,
                    "shoulder_y": shoulder_y,
                    "nose_y": nose_y
                }

            # Toque no peito
            if not toque_valido and len(buffer_movimento) >= FRAMES_ANALISE:
                min_index = buffer_movimento.index(max(buffer_movimento))
                descendo = all(buffer_movimento[i] <= buffer_movimento[i + 1] + TOLERANCIA_MOVIMENTO for i in range(min_index))
                subindo = all(buffer_movimento[i] >= buffer_movimento[i + 1] - TOLERANCIA_MOVIMENTO for i in range(min_index, len(buffer_movimento) - 1))
                if max(buffer_movimento) >= (shoulder_y + MARGEM_PEITO) and descendo and subindo:
                    toque_valido = True

            # Extensão dos cotovelos
            if toque_valido and not extensao_valida:
                if lado_analise == "esquerdo":
                    a = ponto_em_pixels(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], w, h)
                    b = ponto_em_pixels(lm[mp_pose.PoseLandmark.LEFT_ELBOW], w, h)
                    c = ponto_em_pixels(lm[mp_pose.PoseLandmark.LEFT_WRIST], w, h)
                else:
                    a = ponto_em_pixels(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER], w, h)
                    b = ponto_em_pixels(lm[mp_pose.PoseLandmark.RIGHT_ELBOW], w, h)
                    c = ponto_em_pixels(lm[mp_pose.PoseLandmark.RIGHT_WRIST], w, h)

                angulo = calcular_angulo(a, b, c)
                if angulo > ANGULO_MINIMO_EXTENSAO:
                    extensao_valida = True

            # Contato com o banco
            contatos["pes"] = ankle_y >= frame_inicial["ankle_y"] - TOLERANCIA_CONTATO
            contatos["gluteo"] = hip_y >= frame_inicial["hip_y"] - TOLERANCIA_CONTATO
            contatos["ombros"] = shoulder_y >= frame_inicial["shoulder_y"] - TOLERANCIA_CONTATO
            contatos["cabeca"] = nose_y >= frame_inicial["nose_y"] - TOLERANCIA_CONTATO

    cap.release()

    # Retorno estruturado para API
    resultado = []

    resultado.append("✅ Toque no peito – a barra chegou à altura adequada." if toque_valido
                     else "❌ Toque no peito ausente – a barra não chegou à altura mínima do tórax com controle.")

    resultado.append("✅ Extensão dos cotovelos – finalização completa do movimento." if extensao_valida
                     else "❌ Extensão dos cotovelos incompleta – os braços não foram estendidos após o toque.")

    resultado.append("✅ Pés no chão – os pés permaneceram firmes no solo." if contatos["pes"]
                     else "❌ Pés fora do chão – houve perda de contato com o solo.")

    resultado.append("✅ Glúteo no banco – contato mantido durante a execução." if contatos["gluteo"]
                     else "❌ Glúteo fora do banco – houve elevação ou perda de contato.")

    resultado.append("✅ Ombros no banco – estabilidade adequada na parte superior." if contatos["ombros"]
                     else "❌ Ombros fora do banco – instabilidade ou levantamento durante a execução.")

    resultado.append("✅ Cabeça no banco – alinhamento técnico mantido." if contatos["cabeca"]
                     else "❌ Cabeça fora do banco – houve elevação da cabeça durante o movimento.")

    return resultado