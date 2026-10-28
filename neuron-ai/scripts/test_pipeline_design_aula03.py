"""
NEURON - Pipeline da Aula 03 de Design de Artefatos Digitais.

ATENCAO: as paginas multimodais (16 a 19, segundo o diagnostico)
geram chamadas ao OpenRouter e consomem creditos.

Protecao: se o arquivo de saida ja existir, o script NAO reprocessa
(para nao pagar duas vezes). Para refazer, apague o JSON de saida.

Como executar (na pasta neuron-ai, com o .venv correto ativo):

    python -m scripts.test_pipeline_design_aula03
"""

import sys
from pathlib import Path

from app.rag.discipline_processor import DisciplineProcessor


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PASTA_AULA = Path(
    "materiais_academicos/"
    "periodo_03/"
    "design_de_artefatos_digitais/"
    "aula_03_publico_alvo"
)

ARQUIVO_SAIDA = Path(
    "saidas_testes/"
    "design_aula_03_pipeline_completa.json"
)

PERIODO = "03"
DISCIPLINA = "design_de_artefatos_digitais"
ASSUNTO = "publico_alvo"
AULA = "03"


print("=" * 80)
print("PIPELINE RAG - DESIGN DE ARTEFATOS DIGITAIS - AULA 03")
print("=" * 80)

if ARQUIVO_SAIDA.exists():
    print(
        f"\nO arquivo de saida ja existe: {ARQUIVO_SAIDA}\n"
        "Nada foi processado (nenhuma API foi chamada).\n"
        "Para refazer, apague esse arquivo e rode de novo."
    )
    sys.exit(0)

print(f"\nAssunto: {ASSUNTO}")
print(f"Periodo: {PERIODO}")
print(f"Disciplina: {DISCIPLINA}")
print(
    "\nATENCAO: paginas multimodais geram chamadas ao OpenRouter."
)
print("\nIniciando processamento...")


processor = DisciplineProcessor(
    chunk_size=1000,
    chunk_overlap=150
)

resultado = processor.processar_aula(
    pasta_aula=PASTA_AULA,
    periodo=PERIODO,
    disciplina=DISCIPLINA,
    assunto=ASSUNTO,
    aula=AULA
)

processor.salvar_json(
    resultado,
    ARQUIVO_SAIDA
)


resumo = resultado["resumo"]

print("\n" + "=" * 80)
print("RESUMO DA INGESTAO")
print("=" * 80)

print(f"Arquivo: {resumo['arquivo']}")
print(f"Total de paginas: {resumo['total_paginas']}")
print(f"Paginas textuais: {resumo['paginas_textuais']}")
print(f"Paginas multimodais: {resumo['paginas_multimodais']}")
print(f"Chunks gerados: {resumo['total_chunks']}")
print(f"Chunk size: {resumo['chunk_size']}")
print(f"Chunk overlap: {resumo['chunk_overlap']}")


print("\n" + "=" * 80)
print("PAGINAS PROCESSADAS")
print("=" * 80)

for pagina in resultado["paginas"]:

    metadata = pagina["metadata"]

    print(
        f"pag {metadata['pagina']:2} | "
        f"{metadata['tipo_extracao']:10} | "
        f"texto original: {metadata['caracteres_texto_original']:4} | "
        f"conteudo final: {len(pagina['conteudo']):4}"
    )


print("\n" + "=" * 80)
print("CONTEUDO DAS PAGINAS MULTIMODAIS (para conferir a qualidade)")
print("=" * 80)

for pagina in resultado["paginas"]:

    metadata = pagina["metadata"]

    if metadata["tipo_extracao"] != "multimodal":
        continue

    print("\n" + "-" * 80)
    print(f"PAGINA {metadata['pagina']}")
    print("-" * 80)
    print(pagina["conteudo"][:800] or "(vazio)")


print("\n" + "=" * 80)
print(f"Saida salva em: {ARQUIVO_SAIDA}")
print("=" * 80)