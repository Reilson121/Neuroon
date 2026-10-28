import json
import sys
from pathlib import Path

from app.rag.embedding_processor import EmbeddingProcessor
from app.rag.vector_store import VectorStore


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Uso:
#   python -m scripts.persistir_chunks
#   python -m scripts.persistir_chunks caminho\outro_arquivo.json
ARQUIVO = Path(
    sys.argv[1]
    if len(sys.argv) > 1
    else "saidas_testes/"
         "estrutura_de_dados_avancada_aula_0_aula_1_aula_2.json"
)

print("=" * 80)
print("PERSISTENCIA DE CHUNKS NO POSTGRESQL + PGVECTOR")
print("=" * 80)
print(f"Arquivo: {ARQUIVO}")

with open(ARQUIVO, encoding="utf-8") as arquivo:
    dados = json.load(arquivo)

chunks = dados["chunks"]
disciplina = dados["disciplina"]

print(f"Disciplina: {disciplina}")
print(f"Chunks no JSON: {len(chunks)}")

embedder = EmbeddingProcessor()
store = VectorStore()

if embedder.dimensions != store.dimensao:
    raise SystemExit(
        f"Modelo gera {embedder.dimensions} dimensões; "
        f"a tabela espera {store.dimensao}."
    )

print("\nGerando embeddings...")
com_embedding = embedder.processar_chunks(chunks)

print(f"Embeddings gerados: {len(com_embedding)}")

salvos = store.salvar_chunks(com_embedding)

print("\n" + "=" * 80)
print("RESULTADO")
print("=" * 80)
print(f"Chunks salvos (insert/update): {salvos}")
print(f"Total no banco para a disciplina: {store.contar(disciplina)}")

print("\nChunks por assunto no banco:")
for assunto, total, arquivos in store.resumo_por_assunto(disciplina):
    print(f"  {assunto:32s} chunks={total:3d} arquivos={arquivos}")
