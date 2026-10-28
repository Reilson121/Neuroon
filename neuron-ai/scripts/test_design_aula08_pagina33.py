"""
NEURON - Diagnostico da pagina 33 da Aula 08 (resposta vazia).

Repete a MESMA chamada de visao que o DocumentProcessor faz
(mesmo prompt, mesma imagem) e mostra a resposta crua do modelo:
motivo de parada, uso de tokens e campos da mensagem.

ATENCAO: faz 1 chamada ao OpenRouter (consome creditos).
NAO altera nenhum componente do projeto e NAO grava arquivos.
A chave de API nao e exibida.

Como executar (na pasta neuron-ai, com o .venv correto ativo):

    python -m scripts.test_design_aula08_pagina33
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


print("=" * 80)
print("DIAGNOSTICO - AULA 08, PAGINA 33 (resposta vazia)")
print("=" * 80)

processor = DocumentProcessor()

print(f"\nModelo de visao: {processor.vision_model}")

client = processor.obter_cliente()

# "Espiao": guarda a resposta crua sem alterar o comportamento.
capturado = {}

criar_original = client.chat.completions.create


def criar_com_espiao(*args, **kwargs):
    resposta = criar_original(*args, **kwargs)
    capturado["resposta"] = resposta
    return resposta


client.chat.completions.create = criar_com_espiao


documento = pymupdf.open(PDF)
pagina = documento[NUMERO_PAGINA - 1]

print(f"Pagina: {NUMERO_PAGINA}")
print("\nChamando o modelo de visao (1 chamada)...")

conteudo = processor.analisar_pagina_visual(pagina)

documento.close()

print("\n" + "=" * 80)
print("RESULTADO")
print("=" * 80)

print(f"Tamanho do conteudo devolvido: {len(conteudo)} caracteres")

resposta = capturado.get("resposta")

if resposta is None:
    print(
        "\nNao foi possivel capturar a resposta crua "
        "(o espiao nao foi acionado)."
    )

else:
    escolha = resposta.choices[0]

    print(f"finish_reason: {escolha.finish_reason}")
    print(f"usage: {resposta.usage}")

    mensagem = escolha.message.model_dump()

    print("\nCampos da mensagem:")

    for campo, valor in mensagem.items():

        texto = repr(valor)

        if len(texto) > 400:
            texto = texto[:400] + "... (cortado)"

        print(f"  {campo}: {texto}")

print("\n" + "=" * 80)
print("DIAGNOSTICO CONCLUIDO")
print("=" * 80)