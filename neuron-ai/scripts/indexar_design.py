"""Indexa o corpus validado de Design; embeddings calculados localmente."""

import json
import sys

from app.rag.design_corpus import DISCIPLINA, carregar_validado


def main():
    from app.rag.index_sync import sincronizar_indice
    from app.rag.vector_store import VectorStore

    dados = carregar_validado()
    resultado = sincronizar_indice(VectorStore(), dados["chunks"], DISCIPLINA,
                                   permitir_insercao=True)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Indexação não concluída ({type(erro).__name__}). "
              "Confira o corpus e a conexão local com o banco.", file=sys.stderr)
        sys.exit(1)
