"""Contratos internos da prática, chamados exclusivamente pelo Spring Boot."""

from threading import Lock
import logging
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from app.api.internal_auth import exigir_token_interno
from app.practice.service import PracticeService, PracticeError

router = APIRouter(prefix="/internal/v1/practice", tags=["Prática interna"], dependencies=[Depends(exigir_token_interno)])
_service = None
_lock = Lock()
Id = Annotated[int, Field(gt=0, strict=True)]
Sessao = Annotated[str, Field(pattern=r"^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$")]


class PracticeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    sessao_id: Sessao
    usuario_id: Id
    disciplina_id: Id
    assunto_id: Id | None = None
    assunto_ids: list[Id] = Field(default_factory=list, max_length=20)
    origem: Literal["LISTA", "PROVA", "MISTO"] = "MISTO"
    modo: Literal["CADASTRADAS", "GERADAS_IA"] = "CADASTRADAS"
    quantidade: int = Field(ge=1, le=10)
    material_ids: list[Id] = Field(max_length=100)
    excluir_fingerprints: list[str] = Field(default_factory=list, max_length=200)
    tipo_questao: Literal['MISTO','CONCEITUAL','TESTE_MESA','LOGICA','ESTILO_PROFESSOR'] = 'MISTO'
    nivel_contexto: Literal['DIRETO','COTIDIANO','DETALHADO'] = 'COTIDIANO'
    unidade_calculo: Literal[0,1,2] = 0
    topico_calculo: Annotated[str, Field(pattern=r'^[a-z_]{1,40}$|^MISTO$')] = 'MISTO'
    tipo_funcao: Literal['MISTO','AFIM','POLINOMIAL','RACIONAL','RADICAL','POR_PARTES','TRIGONOMETRICA','EXPONENCIAL','LOGARITMICA','HIPERBOLICA','IMPLICITA'] = 'MISTO'


class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    sessao_id: Sessao
    usuario_id: Id
    questao_id: Sessao
    alternativa: Literal["A", "B", "C", "D", "E"]
    material_ids: list[Id] = Field(max_length=100)


def obter_service():
    global _service
    with _lock:
        if _service is None:
            _service = PracticeService()
    return _service


def executar(acao):
    try:
        return acao()
    except PracticeError as e:
        raise HTTPException(e.status, detail={"codigo": e.codigo, "mensagem": e.mensagem}) from None
    except Exception as e:
        causas={
            "Formato de contextos inválido.":"CONTEXTOS_FORMATO",
            "Contextos da IA não correspondem aos exercícios.":"CONTEXTOS_QUANTIDADE",
            "Contexto contém dados ou condições não autorizados.":"CONTEXTOS_CONDICOES",
        }
        # Apenas códigos locais e o nome da classe; nunca texto do provedor.
        logging.getLogger(__name__).warning("Prática indisponível: %s (%s)",causas.get(str(e),"FALHA_INTERNA"),type(e).__name__)
        raise HTTPException(503, detail={"codigo": "PRATICA_INDISPONIVEL", "mensagem": "Não foi possível preparar uma prática validada. Tente novamente."}) from None


@router.post("/questions")
def questions(req: PracticeRequest):
    return executar(lambda: obter_service().montar_questoes(req.model_dump()))


@router.post("/answers")
def answers(req: AnswerRequest):
    return executar(lambda: obter_service().corrigir(req.model_dump()))
