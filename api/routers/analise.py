from fastapi import APIRouter, UploadFile, File, Form
from api.services.processamento import processar_video
from api.utils.arquivos import salvar_video_temporario

router = APIRouter()

@router.post("/")
async def analisar(
    nome: str = Form(...),
    email: str = Form(...),
    movimento: str = Form(...),  # "squat", "bench" ou "deadlift"
    video: UploadFile = File(...)
):
    caminho_video = await salvar_video_temporario(video)
    resultado = await processar_video(caminho_video, movimento, nome, email)
    return resultado