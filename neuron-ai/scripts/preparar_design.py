"""Consolida as oito aulas e o complemento de Design sem chamadas externas."""

import json
import sys

from app.rag.design_corpus import JSON_CHUNKS, consolidar


def main():
    dados = consolidar()
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    if not JSON_CHUNKS.exists() or JSON_CHUNKS.read_text(encoding="utf-8") != texto:
        temporario = JSON_CHUNKS.with_suffix(".tmp")
        temporario.write_text(texto, encoding="utf-8")
        temporario.replace(JSON_CHUNKS)
    print(json.dumps({k: v for k, v in dados.items() if k not in {"paginas", "chunks", "arquivos"}},
                     ensure_ascii=False, indent=2))
    print(f"Corpus conferido: {JSON_CHUNKS}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
