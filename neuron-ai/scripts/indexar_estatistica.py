"""Indexa somente o corpus teórico completo e validado de Estatística."""

import json
import sys


def main():
    from app.rag.estatistica_corpus import DISCIPLINA, carregar_validado
    from app.rag.index_audit import auditar_indice
    from app.rag.index_sync import sincronizar_indice
    from app.rag.vector_store import VectorStore

    # Uma prévia parcial não passa pela conferência de cobertura do mapa.
    dados = carregar_validado()
    store = VectorStore()
    resultado = sincronizar_indice(store, dados["chunks"], DISCIPLINA, permitir_insercao=True, tipos_material=["SLIDE_AULA"])
    auditoria = auditar_indice(store, dados["chunks"], DISCIPLINA, tipos_material=["SLIDE_AULA"])
    if not auditoria["compativel"]:
        raise RuntimeError("A auditoria posterior à indexação encontrou divergências.")
    print(json.dumps({"sincronizacao": resultado, "indice_compativel": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except Exception as erro:
        print(f"Indexação interrompida ({type(erro).__name__}); confira corpus e banco local.", file=sys.stderr)
        sys.exit(1)
