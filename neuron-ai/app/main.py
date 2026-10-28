from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from starlette.concurrency import run_in_threadpool

from app.api.chat import router as chat_router
from app.api.practice import router as practice_router
from app.api.materials import router as materials_router


@asynccontextmanager
async def ciclo_de_vida(app):
    if os.getenv("NEURON_PRELOAD_MONITOR", "0") == "1":
        from app.api.chat import obter_monitor
        # Carrega o componente existente antes de aceitar chamadas. Não faz
        # perguntas ao provedor e não inicializa um segundo pipeline.
        await run_in_threadpool(obter_monitor)
    yield


app = FastAPI(
    title="NEURON AI Service",
    version="0.1.0",
    lifespan=ciclo_de_vida,
)

app.include_router(chat_router)
app.include_router(practice_router)
app.include_router(materials_router)


@app.exception_handler(RequestValidationError)
async def entrada_invalida(request, erro):
    # A resposta padrão de validação pode repetir valores enviados. Retorna
    # apenas os campos, sem ecoar a pergunta, campos extras ou credenciais.
    campos = sorted({
        ".".join(str(parte) for parte in item["loc"])
        for item in erro.errors()
    })
    return JSONResponse(status_code=422, content={"detail": {
        "codigo": "REQUISICAO_INVALIDA",
        "mensagem": "Confira os campos obrigatórios e seus formatos.",
        "campos": campos,
    }})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "neuron-ai"
    }
