import json
from pathlib import Path

from app.rag.chunk_processor import ChunkProcessor


ARQUIVO_ENTRADA = Path(
    "saidas_testes/"
    "ideacao_amostra_resultado.json"
)

ARQUIVO_SAIDA = Path(
    "saidas_testes/"
    "ideacao_amostra_chunks.json"
)


print("=" * 80)
print("TESTE DE CHUNKING - NEURON")
print("=" * 80)


# =============================================================
# 1. VERIFICA ARQUIVO
# =============================================================

if not ARQUIVO_ENTRADA.exists():

    print(
        "\nERRO: arquivo de entrada "
        "não encontrado:"
    )

    print(
        ARQUIVO_ENTRADA
    )

    raise SystemExit()


# =============================================================
# 2. CARREGA RESULTADOS DA EXTRAÇÃO
# =============================================================

with open(
    ARQUIVO_ENTRADA,
    "r",
    encoding="utf-8"
) as arquivo:

    resultados = json.load(
        arquivo
    )


print(
    f"\nPáginas carregadas: "
    f"{len(resultados)}"
)


# =============================================================
# 3. CRIA O PROCESSADOR
# =============================================================

processor = ChunkProcessor(
    chunk_size=1000,
    chunk_overlap=150
)


# =============================================================
# 4. GERA OS CHUNKS
# =============================================================

chunks = (
    processor.processar_resultados(
        resultados
    )
)


print(
    f"Chunks gerados: "
    f"{len(chunks)}"
)


# =============================================================
# 5. MOSTRA RESULTADOS POR PÁGINA
# =============================================================

print("\n" + "=" * 80)
print("DISTRIBUIÇÃO DOS CHUNKS")
print("=" * 80)


for item in resultados:

    arquivo_nome = item.get(
        "arquivo",
        "arquivo_desconhecido"
    )

    pagina = item.get(
        "pagina",
        "?"
    )

    chunks_pagina = [
        chunk
        for chunk in chunks
        if (
            chunk["metadata"].get(
                "arquivo"
            )
            == arquivo_nome
            and
            chunk["metadata"].get(
                "pagina"
            )
            == pagina
        )
    ]

    caracteres = len(
        item.get(
            "conteudo",
            ""
        )
    )

    print(
        f"\nPágina {pagina:>2} | "
        f"{arquivo_nome}"
    )

    print(
        f"Caracteres: {caracteres}"
    )

    print(
        f"Chunks: {len(chunks_pagina)}"
    )


# =============================================================
# 6. MOSTRA ALGUNS CHUNKS
# =============================================================

print("\n" + "=" * 80)
print("AMOSTRA DOS CHUNKS")
print("=" * 80)


for chunk in chunks[:8]:

    metadata = chunk[
        "metadata"
    ]

    print("\n" + "-" * 80)

    print(
        f"Chunk ID: "
        f"{chunk['chunk_id']}"
    )

    print(
        f"Arquivo: "
        f"{metadata.get('arquivo')}"
    )

    print(
        f"Página: "
        f"{metadata.get('pagina')}"
    )

    print(
        f"Chunk: "
        f"{metadata.get('chunk_index')}"
        f"/"
        f"{metadata.get('total_chunks_pagina')}"
    )

    print(
        f"Caracteres: "
        f"{metadata.get('chunk_caracteres')}"
    )

    print("\nCONTEÚDO:")

    print(
        chunk["conteudo"]
    )


# =============================================================
# 7. SALVA O RESULTADO
# =============================================================

with open(
    ARQUIVO_SAIDA,
    "w",
    encoding="utf-8"
) as arquivo:

    json.dump(
        chunks,
        arquivo,
        ensure_ascii=False,
        indent=4
    )


print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)

print(
    f"Páginas originais: "
    f"{len(resultados)}"
)

print(
    f"Chunks gerados: "
    f"{len(chunks)}"
)

print(
    f"Chunk size: "
    f"{processor.chunk_size}"
)

print(
    f"Chunk overlap: "
    f"{processor.chunk_overlap}"
)

print(
    "\nArquivo gerado:"
)

print(
    ARQUIVO_SAIDA
)

print("=" * 80)