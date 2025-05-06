from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS") == "True"
)

async def enviar_feedback_email(
    email: EmailStr,
    nome: str,
    movimento: str,
    feedbacks: List[str]
):
    corpo = f"Olá {nome},\n\nSegue abaixo o feedback da sua análise de {movimento.capitalize()}:\n\n"
    corpo += "\n".join(feedbacks)
    corpo += "\n\nObrigado por utilizar nosso sistema de análise técnica!"

    mensagem = MessageSchema(
        subject=f"Feedback da sua análise de {movimento.capitalize()}",
        recipients=[email],
        body=corpo,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(mensagem)