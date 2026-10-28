"""Indexação apenas de fontes locais previamente preparadas e conferidas."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from app.api.internal_auth import exigir_token_interno
from app.practice.material_index import indexar, remover

router=APIRouter(prefix="/internal/v1/materials",tags=["Materiais internos"],dependencies=[Depends(exigir_token_interno)])

class IndexRequest(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    material_id:int=Field(gt=0)

@router.post("/index")
def index(req:IndexRequest):
    try:
        return indexar(req.material_id)
    except ValueError:
        raise HTTPException(409,detail={"codigo":"MATERIAL_NAO_PREPARADO","mensagem":"Confira o cadastro, a autorização e o corpus local do material."}) from None
    except Exception:
        raise HTTPException(503,detail={"codigo":"INDICE_INDISPONIVEL","mensagem":"Não foi possível atualizar o índice."}) from None

@router.post("/{material_id}/reindex")
def reindex(material_id:int):
    return index(IndexRequest(material_id=material_id))

@router.delete("/{material_id}")
def delete(material_id:int):
    if material_id<=0:raise HTTPException(422,detail={"codigo":"ID_INVALIDO"})
    try:return remover(material_id)
    except Exception:raise HTTPException(503,detail={"codigo":"INDICE_INDISPONIVEL","mensagem":"Limpeza do índice pendente."}) from None
