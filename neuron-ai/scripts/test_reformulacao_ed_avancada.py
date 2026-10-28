"""Compara consultas com o mesmo Top-K e filtro, sem chamar o LLM."""

import json
import sys

from scripts.monitor_ed_avancada import DISCIPLINA, JSON_CHUNKS, RAIZ


CONSULTAS = [
    "Como funciona a rotação zig-zag em uma árvore AVL?",
    "rotação zig-zag esquerda-direita",
    "zig-zag",
    "rotações compostas zig-zag",
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from app.rag.index_audit import auditar_indice
    from app.rag.retriever import Retriever
    from app.rag.vector_store import VectorStore

    store = VectorStore()
    chunks = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))["chunks"]
    if not auditar_indice(store, chunks, DISCIPLINA)["compativel"]:
        print("Índice divergente. Teste interrompido.", flush=True)
        return 2
    retriever = Retriever(store=store)
    relatorio = {"disciplina": DISCIPLINA, "k": 5, "assunto": None, "consultas": []}
    for consulta in CONSULTAS:
        resultados = retriever.recuperar(consulta, DISCIPLINA, k=5)
        caso = {"consulta": consulta, "resultados": resultados}
        relatorio["consultas"].append(caso)
        print(consulta, flush=True)
        print([(c["metadata"]["pagina"], round(c["similaridade"], 3)) for c in resultados], flush=True)
    destino = RAIZ / "saidas_testes/comparacao_consultas_zig_zag.json"
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Relatório: {destino}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Teste interrompido ({type(erro).__name__}).", file=sys.stderr)
        sys.exit(1)
