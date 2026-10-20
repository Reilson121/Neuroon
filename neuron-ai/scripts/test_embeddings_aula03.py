import json
from pathlib import Path

import numpy as np

from app.rag.embedding_processor import EmbeddingProcessor


ARQUIVO = Path(
    "saidas_testes/"
    "aula_03_pipeline_completa.json"
)


print("=" * 80)
print("TESTE DE EMBEDDINGS - NEURON")
print("=" * 80)


# =========================================================
# CARREGAR CHUNKS
# =========================================================

with open(
    ARQUIVO,
    "r",
    encoding="utf-8"
) as arquivo:

    dados = json.load(
        arquivo
    )


chunks = dados[
    "chunks"
]


print(
    f"\nChunks carregados: "
    f"{len(chunks)}"
)


# =========================================================
# MODELO
# =========================================================

processor = EmbeddingProcessor()


print(
    f"Dimensões do embedding: "
    f"{processor.dimensions}"
)


# =========================================================
# GERAR EMBEDDINGS
# =========================================================

chunks_com_embeddings = (
    processor.processar_chunks(
        chunks
    )
)


print(
    f"Embeddings gerados: "
    f"{len(chunks_com_embeddings)}"
)


# =========================================================
# PERGUNTA DE TESTE
# =========================================================

pergunta = (
    "Qual é a estrutura básica "
    "de uma história de usuário?"
)


print("\nPergunta:")
print(pergunta)


embedding_pergunta = np.array(
    processor.gerar_embedding(
        pergunta
    )
)


# =========================================================
# SIMILARIDADE
# =========================================================

resultados = []


for chunk in chunks_com_embeddings:

    embedding_chunk = np.array(
        chunk["embedding"]
    )

    # Como os embeddings já estão normalizados,
    # produto escalar equivale à similaridade cosseno.
    similaridade = float(
        np.dot(
            embedding_pergunta,
            embedding_chunk
        )
    )

    resultados.append(
        {
            "similaridade": similaridade,
            "chunk": chunk
        }
    )


resultados = sorted(
    resultados,
    key=lambda x: x[
        "similaridade"
    ],
    reverse=True
)


# =========================================================
# TOP 3
# =========================================================

print("\n" + "=" * 80)
print("TOP 3 RESULTADOS")
print("=" * 80)


for posicao, resultado in enumerate(
    resultados[:3],
    start=1
):

    chunk = resultado[
        "chunk"
    ]

    metadata = chunk[
        "metadata"
    ]

    print("\n" + "-" * 80)

    print(
        f"{posicao}º RESULTADO"
    )

    print(
        f"Similaridade: "
        f"{resultado['similaridade']:.4f}"
    )

    print(
        f"Página: "
        f"{metadata.get('pagina')}"
    )

    print(
        f"Assunto: "
        f"{metadata.get('assunto')}"
    )

    print(
        f"Chunk ID: "
        f"{chunk['chunk_id']}"
    )

    print("\nConteúdo:")

    print(
        chunk["conteudo"][:1000]
    )


print("\n" + "=" * 80)
print("TESTE CONCLUÍDO")
print("=" * 80)