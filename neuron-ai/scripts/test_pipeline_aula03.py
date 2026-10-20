from pathlib import Path

from app.rag.discipline_processor import DisciplineProcessor


PASTA_AULA = Path(
    "materiais_academicos/"
    "periodo_03/"
    "projeto_de_ideacao_de_software/"
    "aula_03_historias_de_usuario"
)

ARQUIVO_SAIDA = Path(
    "saidas_testes/"
    "aula_03_pipeline_completa.json"
)


print("=" * 80)
print("PIPELINE RAG - TESTE DA AULA 03")
print("=" * 80)

print(
    "\nAula: Histórias de Usuário"
)

print(
    "Período: 03"
)

print(
    "Disciplina: projeto_de_ideacao_de_software"
)

print(
    "\nIniciando processamento..."
)

print(
    "ATENÇÃO: páginas multimodais podem "
    "gerar chamadas ao OpenRouter."
)


processor = DisciplineProcessor(
    chunk_size=1000,
    chunk_overlap=150
)


resultado = processor.processar_aula(
    pasta_aula=PASTA_AULA,
    periodo="03",
    disciplina=(
        "projeto_de_ideacao_de_software"
    ),
    assunto=(
        "historias_de_usuario"
    ),
    aula="03"
)


processor.salvar_json(
    resultado,
    ARQUIVO_SAIDA
)


resumo = resultado[
    "resumo"
]


print("\n" + "=" * 80)
print("RESUMO DA INGESTÃO")
print("=" * 80)

print(
    f"Arquivo: "
    f"{resumo['arquivo']}"
)

print(
    f"Total de páginas: "
    f"{resumo['total_paginas']}"
)

print(
    f"Páginas textuais: "
    f"{resumo['paginas_textuais']}"
)

print(
    f"Páginas multimodais: "
    f"{resumo['paginas_multimodais']}"
)

print(
    f"Chunks gerados: "
    f"{resumo['total_chunks']}"
)

print(
    f"Chunk size: "
    f"{resumo['chunk_size']}"
)

print(
    f"Chunk overlap: "
    f"{resumo['chunk_overlap']}"
)


print("\n" + "=" * 80)
print("AMOSTRA DE METADADOS")
print("=" * 80)


for chunk in resultado[
    "chunks"
][:3]:

    metadata = chunk[
        "metadata"
    ]

    print("\n" + "-" * 80)

    print(
        f"Chunk ID: "
        f"{chunk['chunk_id']}"
    )

    print(
        f"Período: "
        f"{metadata.get('periodo')}"
    )

    print(
        f"Disciplina: "
        f"{metadata.get('disciplina')}"
    )

    print(
        f"Assunto: "
        f"{metadata.get('assunto')}"
    )

    print(
        f"Aula: "
        f"{metadata.get('aula')}"
    )

    print(
        f"Página: "
        f"{metadata.get('pagina')}"
    )

    print(
        f"Tipo de extração: "
        f"{metadata.get('tipo_extracao')}"
    )

    print(
        f"Chunk: "
        f"{metadata.get('chunk_index')}"
        f"/"
        f"{metadata.get('total_chunks_pagina')}"
    )

    print(
        "\nConteúdo:"
    )

    print(
        chunk["conteudo"][:700]
    )


print("\n" + "=" * 80)

print(
    "Pipeline concluída."
)

print(
    "\nResultado salvo em:"
)

print(
    ARQUIVO_SAIDA
)

print("=" * 80)