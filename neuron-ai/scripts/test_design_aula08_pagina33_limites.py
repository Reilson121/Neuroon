"""
NEURON - Teste de limites na chamada de visao (Aula 08, pagina 33).

Contexto: a chamada original gastou ~127 mil tokens de RACIOCINIO e
nao devolveu conteudo (finish_reason=length), a um custo de ~US$ 0,11.

Este script repete a chamada da pagina 33 com um teto de tokens de
saida (MAX_TOKENS) e testa 3 variantes de controle do raciocinio:

    A) apenas max_tokens
    B) max_tokens + reasoning effort "low"
    C) max_tokens + reasoning desligado

Os parametros sao injetados por fora (o DocumentProcessor NAO e
alterado). Com MAX_TOKENS = 6000, o pior caso e ~US$ 0,005 por
variante (cerca de US$ 0,015 no total).

Se o provedor recusar algum parametro, o erro e mostrado e o
script segue para a proxima variante.

A chave de API nao e exibida. Nenhum arquivo e gravado.

Como executar (na pasta neuron-ai, com o .venv correto ativo):

    python -m scripts.test_design_aula08_pagina33_limites
"""

import sys
from pathlib import Path

import pymupdf

from app.rag.document_processor import DocumentProcessor


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PDF = Path(
    "materiais_academicos/"
    "periodo_03/"
    "design_de_artefatos_digitais/"
    "aula_08_design_thinking/"
    "AULA_08.pdf"
)

NUMERO_PAGINA = 33
MAX_TOKENS = 6000

VARIANTES = [
    ("A) so max_tokens", None),
    ("B) max_tokens + reasoning effort low", {"effort": "low"}),
    ("C) max_tokens + reasoning desligado", {"enabled": False}),
]


print("=" * 80)
print("TESTE DE LIMITES - AULA 08, PAGINA 33")
print("=" * 80)
print(f"\nmax_tokens: {MAX_TOKENS}")
print("Custo maximo estimado: ~US$ 0,015 no total.")

processor = DocumentProcessor()

print(f"Modelo de visao: {processor.vision_model}")

client = processor.obter_cliente()

criar_original = client.chat.completions.create

# Parametros extras a injetar na proxima chamada.
extras = {}

# Resposta crua da ultima chamada.
capturado = {}


def criar_com_espiao(*args, **kwargs):

    kwargs["max_tokens"] = MAX_TOKENS

    if extras.get("reasoning") is not None:
        kwargs["extra_body"] = {
            "reasoning": extras["reasoning"]
        }

    resposta = criar_original(*args, **kwargs)

    capturado["resposta"] = resposta

    return resposta


client.chat.completions.create = criar_com_espiao


documento = pymupdf.open(PDF)
pagina = documento[NUMERO_PAGINA - 1]


for nome, reasoning in VARIANTES:

    print("\n" + "=" * 80)
    print(f"VARIANTE {nome}")
    print("=" * 80)

    extras["reasoning"] = reasoning
    capturado.clear()

    try:
        conteudo = processor.analisar_pagina_visual(pagina)

    except Exception as erro:
        print(f"ERRO: {type(erro).__name__}")
        print(str(erro)[:500])
        continue

    resposta = capturado.get("resposta")

    print(f"Conteudo devolvido: {len(conteudo)} caracteres")

    if resposta is not None:

        escolha = resposta.choices[0]
        usage = resposta.usage

        detalhes = getattr(
            usage,
            "completion_tokens_details",
            None
        )

        raciocinio = getattr(
            detalhes,
            "reasoning_tokens",
            None
        )

        print(f"finish_reason: {escolha.finish_reason}")
        print(f"completion_tokens: {usage.completion_tokens}")
        print(f"reasoning_tokens: {raciocinio}")
        print(f"custo (US$): {getattr(usage, 'cost', None)}")

    if conteudo:
        print("\nInicio do conteudo:")
        print(conteudo[:600])


documento.close()

print("\n" + "=" * 80)
print("TESTE CONCLUIDO")
print("=" * 80)