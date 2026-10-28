"""Contrato interno do chat, consumido pelo Spring Boot."""

from threading import Lock
from typing import Literal

import psycopg
from fastapi import APIRouter, HTTPException, Depends
from app.api.internal_auth import exigir_token_interno
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


router = APIRouter(prefix="/internal/v1", tags=["Monitor Virtual"], dependencies=[Depends(exigir_token_interno)])
_monitor = None
_inicializacao = Lock()
SLUG = r"^[a-z0-9]+(?:_[a-z0-9]+)*$"


class MensagemContexto(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, strict=True)
    papel: Literal['USUARIO', 'MONITOR']
    conteudo: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, strict=True)

    pergunta: str = Field(min_length=1, max_length=4000)
    disciplina: str = Field(min_length=1, max_length=150, pattern=SLUG)
    assunto: str | None = Field(default=None, min_length=1, max_length=150, pattern=SLUG)
    historico: list[MensagemContexto] = Field(default_factory=list, max_length=8)


class FonteChat(BaseModel):
    # Os metadados adicionais do RAG, inclusive páginas mescladas e IDs futuros,
    # atravessam a API sem serem descartados pelo modelo de resposta.
    model_config = ConfigDict(extra="allow")

    referencia: str = Field(pattern=r"^F[1-9][0-9]*$")
    chunk_id: str
    arquivo: str
    pagina: int = Field(ge=1)
    assunto: str | None = None
    aula: str | None = None
    similaridade: FiniteFloat


class ChatResponse(BaseModel):
    resposta: str
    fontes: list[FonteChat]
    fallback: bool
    motivo: Literal[
        "sem_contexto", "contexto_insuficiente", "geracao_incompleta",
        "formato_invalido", "fontes_invalidas", "tema_nao_identificado",
    ] | None = None
    reformulacoes: int = Field(default=0, ge=0, le=2)
    blocos_sem_fonte_removidos: int = Field(default=0, ge=0)


def obter_monitor():
    """Inicialização tardia: /health e entradas inválidas não carregam o RAG."""
    global _monitor
    with _inicializacao:
        if _monitor is None:
            from app.rag.monitor_virtual import MonitorVirtual
            _monitor = MonitorVirtual()
    return _monitor


def _erro(status, codigo, mensagem):
    return HTTPException(status_code=status, detail={"codigo": codigo, "mensagem": mensagem})


@router.post(
    "/chat", response_model=ChatResponse,
    summary="Responde usando os materiais de uma disciplina",
    responses={
        422: {"description": "Entrada inválida"},
        502: {"description": "Falha no serviço de geração"},
        503: {"description": "Serviço temporariamente indisponível"},
        504: {"description": "Tempo de geração excedido"},
    },
)
def chat(entrada: ChatRequest):
    # Uma rota síncrona usa a fila de threads do FastAPI para não bloquear
    # o processamento assíncrono enquanto o RAG consulta banco/modelo.
    try:
        extras = {'historico': [m.model_dump() for m in entrada.historico]} if entrada.historico else {}
        resultado = obter_monitor().responder(entrada.pergunta, entrada.disciplina, entrada.assunto, **extras)
        return ChatResponse.model_validate(resultado)
    except APITimeoutError:
        raise _erro(504, "IA_TIMEOUT", "O serviço de IA excedeu o tempo de resposta.") from None
    except (APIConnectionError, RateLimitError):
        raise _erro(503, "IA_INDISPONIVEL", "O serviço de IA está temporariamente indisponível.") from None
    except APIStatusError:
        raise _erro(502, "IA_ERRO_PROVEDOR", "Não foi possível concluir a chamada ao serviço de IA.") from None
    except psycopg.Error:
        raise _erro(503, "BASE_INDISPONIVEL", "A base de materiais está temporariamente indisponível.") from None
    except RuntimeError:
        raise _erro(503, "MONITOR_INDISPONIVEL", "O Monitor Virtual está temporariamente indisponível.") from None
    except Exception:
        # Não reflete nem registra mensagens externas, conexões ou credenciais.
        raise _erro(500, "ERRO_INTERNO", "Não foi possível processar a pergunta.") from None
