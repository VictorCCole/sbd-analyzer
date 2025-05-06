import cv2
import mediapipe as mp
import math
from core.utils import ponto_em_pixels, redimensionar, calcular_angulo
import core.config as config

mp_pose = mp.solutions.pose

MARGEM_PEITO = config.MARGEM_PEITO_BENCH
ANGULO_MINIMO_EXTENSAO = config.ANGULO_MINIMO_EXTENSAO_BENCH
FRAMES_ANALISE = config.FRAMES_ANALISE_BENCH
TOLERANCIA_MOVIMENTO = config.TOLERANCIA_MOVIMENTO_BENCH
MAX_WIDTH = config.MAX_WIDTH
MAX_HEIGHT = config.MAX_HEIGHT


def bench(cap):
    pose = mp_pose.Pose(model_complexity=1)

    buffer_movimento = []
    toque_valido = False
    extensao_valida = False

    contato_ombros = True
    contato_gluteo = True
    contato_cabeca = True
    contato_pes = True

    frame_inicial = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            h, w, _ = frame.shape
            lm = results.pose_landmarks.landmark

            # Posições principais
            ankle_y = (lm[mp_pose.PoseLandmark.LEFT_ANKLE].y + lm[mp_pose.PoseLandmark.RIGHT_ANKLE].y) / 2 * h
            hip_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2 * h
            shoulder_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2 * h
            nose_y = lm[mp_pose.PoseLandmark.NOSE].y * h

            wrist_esq_y = lm[mp_pose.PoseLandmark.LEFT_WRIST].y * h
            wrist_dir_y = lm[mp_pose.PoseLandmark.RIGHT_WRIST].y * h
            barra_y = (wrist_esq_y + wrist_dir_y) / 2

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

            # Toque no peito detectado por descida + subida + profundidade
            if not toque_valido and len(buffer_movimento) >= FRAMES_ANALISE:
                min_index = buffer_movimento.index(max(buffer_movimento))
                descendo = all(buffer_movimento[i] <= buffer_movimento[i + 1] + TOLERANCIA_MOVIMENTO for i in range(min_index))
                subindo = all(buffer_movimento[i] >= buffer_movimento[i + 1] - TOLERANCIA_MOVIMENTO for i in range(min_index, len(buffer_movimento) - 1))
                if max(buffer_movimento) >= (shoulder_y + MARGEM_PEITO) and descendo and subindo:
                    toque_valido = True

            # Extensão dos braços após toque válido
            if toque_valido and not extensao_valida:
                a = ponto_em_pixels(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], w, h)
                b = ponto_em_pixels(lm[mp_pose.PoseLandmark.LEFT_ELBOW], w, h)
                c = ponto_em_pixels(lm[mp_pose.PoseLandmark.LEFT_WRIST], w, h)
                angulo = calcular_angulo(a, b, c)
                if angulo > ANGULO_MINIMO_EXTENSAO:
                    extensao_valida = True

            # CONTATO COM O BANCO E O CHÃO
            contato_pes = ankle_y >= frame_inicial["ankle_y"] - 5
            contato_gluteo = hip_y >= frame_inicial["hip_y"] - 5
            contato_ombros = shoulder_y >= frame_inicial["shoulder_y"] - 5
            contato_cabeca = nose_y >= frame_inicial["nose_y"] - 5

        # Exibição
        frame_show = redimensionar(frame, MAX_WIDTH, MAX_HEIGHT)
        y = 40
        def show(fb, ok):
            cor = (0, 255, 0) if ok else (0, 0, 255)
            texto = f"✅ {fb}" if ok else f"❌ {fb}"
            nonlocal y
            cv2.putText(frame_show, texto, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)
            y += 35

        show("Toque no peito", toque_valido)
        show("Extensão dos cotovelos", extensao_valida)
        show("Pés no chão", contato_pes)
        show("Glúteo no banco", contato_gluteo)
        show("Ombros no banco", contato_ombros)
        show("Cabeça no banco", contato_cabeca)

        cv2.imshow("Bench Press - IPF Check", frame_show)
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
