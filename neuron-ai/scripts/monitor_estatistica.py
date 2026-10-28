"""Conferência e execução do Monitor Virtual existente para Estatística."""

import argparse
import json
import sys


def main(argv=None):
    from app.rag.mapas.estatistica import ORDEM_ASSUNTOS

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pergunta", nargs="?", default="O que é probabilidade condicional?")
    parser.add_argument("--assunto", choices=ORDEM_ASSUNTOS)
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--verificar-base", action="store_true")
    modo.add_argument("--somente-busca", action="store_true")
    args = parser.parse_args(argv)
    from app.rag.estatistica_corpus import DISCIPLINA, carregar_validado
    from app.rag.index_audit import auditar_indice
    from app.rag.vector_store import VectorStore

    dados = carregar_validado()
    store = VectorStore()
    auditoria = auditar_indice(store, dados["chunks"], DISCIPLINA, tipos_material=["SLIDE_AULA"])
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in auditoria.items()}, ensure_ascii=False))
    if not auditoria["compativel"]:
        return 2
    if args.verificar_base:
        return 0
    from app.rag.retriever import Retriever
    retriever = Retriever(store=store)
    if args.somente_busca:
        resultado = retriever.recuperar(args.pergunta, DISCIPLINA, args.assunto, k=5)
    else:
        from app.rag.monitor_virtual import MonitorVirtual
        resultado = MonitorVirtual(retriever).responder(args.pergunta, DISCIPLINA, args.assunto)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Monitor interrompido ({type(erro).__name__}); confira corpus e configurações.", file=sys.stderr)
        sys.exit(1)
