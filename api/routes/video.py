from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uuid
import shutil
from api.services.processamento import processar_agachamento

router = APIRouter()

@router.post("/")
async def analisar_video(
    tipo_movimento: str = Form(...),
    arquivo: UploadFile = File(...)
):
    if tipo_movimento != "agachamento":
        return JSONResponse(status_code=400, content={"erro": "Movimento não suportado ainda."})

    # Gera nome único pro vídeo
    nome_arquivo = f"{uuid.uuid4()}.mp4"
    caminho = f"media/{nome_arquivo}"

    # Salva o vídeo
    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    # Processa o vídeo
    feedback = processar_agachamento(caminho)

    return {"movimento": tipo_movimento, "feedback": feedback}
