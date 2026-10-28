"""Atualiza o índice de ED Avançada usando o JSON já processado e validado."""

import json
import sys

from scripts.monitor_ed_avancada import DISCIPLINA, JSON_CHUNKS


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from app.rag.index_sync import sincronizar_indice
    from app.rag.vector_store import VectorStore

    dados = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))
    print("Sincronizando os chunks das Aulas 0, 1 e 2 de Estrutura de Dados Avançada.")
    print("Embeddings de textos alterados serão recalculados localmente.")
    resumo = sincronizar_indice(VectorStore(), dados["chunks"], DISCIPLINA)
    print("Sincronização concluída e conferida:")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erro:
        # Não expõe configuração de conexão nem mensagens de bibliotecas externas.
        print(f"Sincronização não concluída ({type(erro).__name__}). "
              "Execute --verificar-base no comando do monitor para conferir "
              "o estado da base e envie as saídas para diagnóstico.", file=sys.stderr)
        sys.exit(1)
