import uuid
import shutil
from fastapi import UploadFile

async def salvar_video_temporario(video: UploadFile) -> str:
    filename = f"temp_{uuid.uuid4()}.mp4"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    return filename
