"""Consolida as cinco aulas de Ideação sem chamadas externas."""

import json
import sys
from app.rag.ideacao_corpus import JSON_CHUNKS, consolidar, salvar_json


def main():
    dados = consolidar()
    salvar_json(JSON_CHUNKS, dados)
    print(json.dumps({k: v for k, v in dados.items() if k not in {"paginas", "chunks", "arquivos"}},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
