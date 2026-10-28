"""Monitor Virtual de Design de Artefatos Digitais, com fontes reais."""

import argparse
import json
import sys

from app.rag.design_corpus import AULAS, DISCIPLINA, carregar_validado


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pergunta", nargs="?", default="O que é um artefato digital?")
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--verificar-base", action="store_true")
    modo.add_argument("--somente-busca", action="store_true")
    parser.add_argument("--assunto", choices=[v[1] for v in AULAS.values()])
    parser.add_argument("--top-k", type=int, choices=range(1, 51), default=5, metavar="1..50")
    parser.add_argument("--similaridade-minima", type=float, default=0.25)
    args = parser.parse_args(argv)
    from app.rag.index_audit import auditar_indice
    from app.rag.vector_store import VectorStore

    dados = carregar_validado()
    store = VectorStore()
    auditoria = auditar_indice(store, dados["chunks"], DISCIPLINA)
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in auditoria.items()},
                     ensure_ascii=False, indent=2))
    if not auditoria["compativel"]:
        print("Execute scripts.indexar_design para sincronizar o corpus validado.")
        return 2
    if args.verificar_base:
        return 0
    from app.rag.retriever import Retriever
    retriever = Retriever(store=store)
    if args.somente_busca:
        for item in retriever.recuperar(args.pergunta, DISCIPLINA, args.assunto, k=args.top_k):
            m = item["metadata"]
            print(f"\n{m['arquivo']} | p. {m['pagina']} | {m['assunto']} | "
                  f"similaridade={item['similaridade']:.3f}\n{item['conteudo']}")
        return 0
    from app.rag.monitor_virtual import MonitorVirtual
    monitor = MonitorVirtual(retriever, k=args.top_k, similaridade_minima=args.similaridade_minima)
    resultado = monitor.responder(args.pergunta, DISCIPLINA, args.assunto)
    print("\n" + resultado["resposta"])
    if resultado["fallback"]:
        print(f"Motivo: {resultado['motivo']}")
    for fonte in resultado["fontes"]:
        paginas = sorted(set([fonte["pagina"], *fonte.get("paginas_mescladas", [])]))
        print(f"[{fonte['referencia']}] {fonte['arquivo']} | páginas {', '.join(map(str, paginas))} | "
              f"aula {fonte['aula']} | {fonte['assunto']}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Monitor não concluído ({type(erro).__name__}). "
              "Confira o corpus e as conexões configuradas.", file=sys.stderr)
        sys.exit(1)
