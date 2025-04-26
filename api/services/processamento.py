from core import squat
import cv2
import mediapipe as mp

def processar_agachamento(caminho_video: str):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(caminho_video)
    resultados = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            h, w, _ = frame.shape
            feedback = squat.analisar(frame, results.pose_landmarks.landmark, h, w)
            resultados.append(feedback)

    cap.release()

    # Retorna o último frame analisado como exemplo
    return resultados[-1] if resultados else {"erro": "Sem pose detectada"}
