"""
NEURON - Ingestao de aulas de Design de Artefatos Digitais.

Uso (na pasta neuron-ai, com o .venv correto ativo):

    python -m scripts.ingerir_aula_design 04

Codigos aceitos: 01, 02, 03, 04, 05, 06, 07, 08, complementar.

ATENCAO: paginas multimodais geram chamadas ao OpenRouter e
consomem creditos (com o teto de tokens e o raciocinio desligado
do DocumentProcessor, cada chamada custa uma fracao de centavo).

Protecao: se o JSON de saida da aula ja existir, o script NAO
reprocessa. Para refazer, apague o JSON de saida.
"""

import sys
from pathlib import Path

from app.rag.discipline_processor import DisciplineProcessor


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


BASE = Path(
    "materiais_academicos/"
    "periodo_03/"
    "design_de_artefatos_digitais"
)

PERIODO = "03"
DISCIPLINA = "design_de_artefatos_digitais"

# codigo -> (pasta da aula, assunto)
AULAS = {
    "01": ("aula_01_introducao_ao_design", "introducao_ao_design"),
    "02": ("aula_02_ferramentas_visuais", "ferramentas_visuais"),
    "03": ("aula_03_publico_alvo", "publico_alvo"),
    "04": (
        "aula_04_comportamento_do_consumidor",
        "comportamento_do_consumidor",
    ),
    "05": ("aula_05_design_de_interface", "design_de_interface"),
    "06": ("aula_06_principios_de_design", "principios_de_design"),
    "07": (
        "aula_07_design_de_interface_diagramacao",
        "design_de_interface_diagramacao",
    ),
    "08": ("aula_08_design_thinking", "design_thinking"),
    "complementar": (
        "material_complementar_matriz_csd",
        "matriz_csd",
    ),
}


if len(sys.argv) != 2 or sys.argv[1] not in AULAS:
    print("Uso: python -m scripts.ingerir_aula_design <codigo>")
    print("Codigos aceitos:", ", ".join(AULAS))
    sys.exit(1)


CODIGO = sys.argv[1]
PASTA, ASSUNTO = AULAS[CODIGO]

PASTA_AULA = BASE / PASTA

ARQUIVO_SAIDA = Path(
    f"saidas_testes/design_aula_{CODIGO}_pipeline_completa.json"
)


print("=" * 80)
print(f"INGESTAO - DESIGN DE ARTEFATOS DIGITAIS - AULA {CODIGO}")
print("=" * 80)

if ARQUIVO_SAIDA.exists():
    print(
        f"\nO arquivo de saida ja existe: {ARQUIVO_SAIDA}\n"
        "Nada foi processado (nenhuma API foi chamada).\n"
        "Para refazer, apague esse arquivo e rode de novo."
    )
    sys.exit(0)

if not PASTA_AULA.exists():
    raise FileNotFoundError(
        f"Pasta da aula nao encontrada: {PASTA_AULA}"
    )

print(f"\nPasta: {PASTA}")
print(f"Assunto: {ASSUNTO}")
print(f"Periodo: {PERIODO}")
print(f"Disciplina: {DISCIPLINA}")
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
    aula=CODIGO
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

alertas = []

for pagina in resultado["paginas"]:

    metadata = pagina["metadata"]
    motivos = metadata["motivos_deteccao"]

    print(
        f"pag {metadata['pagina']:2} | "
        f"{metadata['tipo_extracao']:10} | "
        f"texto original: {metadata['caracteres_texto_original']:4} | "
        f"conteudo final: {len(pagina['conteudo']):4} | "
        f"{', '.join(motivos)}"
    )

    if "multimodal_vazio_fallback_textual" in motivos:
        alertas.append(
            f"pag {metadata['pagina']}: visao vazia, "
            "usado o texto real"
        )

    if not pagina["conteudo"].strip():
        alertas.append(
            f"pag {metadata['pagina']}: SEM CONTEUDO "
            "(nenhum chunk sera gerado)"
        )


print("\n" + "=" * 80)
print("ALERTAS")
print("=" * 80)

if alertas:
    for alerta in alertas:
        print(f"- {alerta}")
else:
    print("Nenhum alerta.")


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