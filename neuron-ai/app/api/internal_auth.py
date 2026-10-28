"""Autenticação de serviço para as novas operações internas."""

import hmac
import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()


def exigir_token_interno(x_internal_token: str | None = Header(default=None, alias="X-Internal-Token")):
    esperado = os.getenv("NEURON_INTERNAL_TOKEN")
    if not esperado:
        raise HTTPException(503, detail={"codigo": "SERVICO_NAO_CONFIGURADO", "mensagem": "Configure a autenticação interna."})
    if x_internal_token is None or not hmac.compare_digest(x_internal_token, esperado):
        raise HTTPException(401, detail={"codigo": "ACESSO_INTERNO_NEGADO", "mensagem": "Autenticação interna necessária."})
