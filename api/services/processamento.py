import cv2
from core import squat, bench, deadlift
from api.services.email_service import enviar_feedback_email

async def processar_video(caminho_video, movimento, nome, email):
    cap = cv2.VideoCapture(caminho_video)
    feedbacks = []

    if movimento == "squat":
        feedbacks = squat.analisar_squat(cap)  # deve retornar uma lista de strings
    elif movimento == "bench":
        feedbacks = bench.bench(cap)
    elif movimento == "deadlift":
        feedbacks = deadlift.analisar_deadlift(cap)

    await enviar_feedback_email(
        email=email,
        nome=nome,
        movimento=movimento,
        feedbacks=feedbacks
    )

    return {"status": "Análise concluída", "feedbacks": feedbacks}
