from fastapi import FastAPI
from api.routers import analise

app = FastAPI(
    title="Análise de Powerlifting",
    description="API para análise de movimentos: agachamento, supino e levantamento terra",
    version="1.0.0"
)

# Inclui o roteador com prefixo /analisar
app.include_router(analise.router, prefix="/analisar", tags=["Análise"])
