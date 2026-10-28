"""
NEURON - Diagnostico de Design de Artefatos Digitais (SEM API).

Mostra, para cada PDF, quais paginas o detector marcaria como
multimodais. Nao chama o OpenRouter e nao gera custo.

Como executar (na pasta neuron-ai, com o .venv ativo):

    python -m scripts.test_design_detector
"""

import sys
from pathlib import Path

import pymupdf

from app.rag.document_processor import DocumentProcessor


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PASTA_DISCIPLINA = Path(
    "materiais_academicos/"
    "periodo_03/"
    "design_de_artefatos_digitais"
)


processor = DocumentProcessor()

arquivos = sorted(
    PASTA_DISCIPLINA.rglob("*.pdf")
)

if not arquivos:
    raise FileNotFoundError(
        f"Nenhum PDF encontrado em: {PASTA_DISCIPLINA}"
    )


print("=" * 75)
print("DIAGNOSTICO - DESIGN DE ARTEFATOS DIGITAIS")
print("=" * 75)


total_geral_paginas = 0
total_geral_multimodais = 0


for arquivo in arquivos:

    print(
        f"\nPASTA:   {arquivo.parent.name}"
    )
    print(
        f"ARQUIVO: {arquivo.name}"
    )

    documento = pymupdf.open(arquivo)

    total_paginas = len(documento)

    paginas_textuais = []
    paginas_multimodais = []

    for numero_pagina, pagina in enumerate(
        documento,
        start=1
    ):

        texto = processor.extrair_texto_pagina(pagina)

        resultado = processor.precisa_multimodal(
            pagina,
            texto
        )

        if resultado["precisa_multimodal"]:
            paginas_multimodais.append(numero_pagina)

        else:
            paginas_textuais.append(numero_pagina)

    documento.close()

    total_geral_paginas += total_paginas
    total_geral_multimodais += len(paginas_multimodais)

    print(f"Total de paginas: {total_paginas}")
    print(f"Paginas textuais: {len(paginas_textuais)}")
    print(f"Paginas multimodais: {len(paginas_multimodais)}")
    print(f"Candidatas multimodais: {paginas_multimodais}")
    print("-" * 75)


print("\n" + "=" * 75)
print("RESUMO DA DISCIPLINA")
print("=" * 75)
print(f"PDFs analisados: {len(arquivos)}")
print(f"Total de paginas: {total_geral_paginas}")
print(
    f"Paginas que iriam para o modelo de visao: "
    f"{total_geral_multimodais}"
)

print("\nDIAGNOSTICO CONCLUIDO (nenhuma API foi chamada)")