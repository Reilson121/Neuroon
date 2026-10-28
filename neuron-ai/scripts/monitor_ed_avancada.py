"""Validação e execução do Monitor Virtual de Estrutura de Dados Avançada."""

import argparse
import json
import sys
from pathlib import Path


DISCIPLINA = "estrutura_de_dados_avancada"
RAIZ = Path(__file__).resolve().parents[1]
JSON_CHUNKS = RAIZ / "saidas_testes/estrutura_de_dados_avancada_aula_0_aula_1_aula_2.json"


def criar_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pergunta", nargs="?", default="O que é uma fila de prioridade?")
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--verificar-base", action="store_true", help="Só compara JSON e banco; não chama a IA.")
    modo.add_argument("--somente-busca", action="store_true", help="Testa recuperação sem chamar o LLM.")
    parser.add_argument("--assunto", help="Slug do assunto para filtrar a recuperação.")
    parser.add_argument("--top-k", type=int, choices=range(1, 51), default=5, metavar="1..50")
    parser.add_argument("--similaridade-minima", type=float, default=0.25,
                        help="Limiar experimental da demo; ainda depende de calibração.")
    return parser


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = criar_parser().parse_args(argv)
    # Só importa configurações e abre o banco quando o comando é executado.
    from app.rag.index_audit import auditar_indice
    from app.rag.vector_store import VectorStore

    store = VectorStore()
    dados = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))
    relatorio = auditar_indice(store, dados["chunks"], DISCIPLINA)
    resumo = {k: len(v) if isinstance(v, list) else v for k, v in relatorio.items()}
    print("Verificação do índice (somente leitura):")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    if not relatorio["compativel"]:
        print("O índice difere dos chunks processados. Nada foi alterado.")
        print("Envie este resumo para validarmos a atualização antes de testar as respostas.")
        return 2
    if args.verificar_base:
        return 0

    from app.rag.retriever import Retriever
    retriever = Retriever(store=store)
    if args.somente_busca:
        for indice, item in enumerate(retriever.recuperar(
            args.pergunta, DISCIPLINA, args.assunto, k=args.top_k
        ), start=1):
            metadata = item["metadata"]
            print(f"\n{indice}. {metadata['arquivo']} | p. {metadata['pagina']} | "
                  f"{metadata.get('assunto')} | sim={item['similaridade']:.3f}")
            if metadata.get("paginas_mescladas"):
                print(f"Páginas mescladas: {metadata['paginas_mescladas']}")
            print(item["conteudo"])
        return 0

    from app.rag.monitor_virtual import MonitorVirtual
    monitor = MonitorVirtual(retriever, k=args.top_k,
                             similaridade_minima=args.similaridade_minima)
    resultado = monitor.responder(args.pergunta, DISCIPLINA, args.assunto)
    print("\n" + resultado["resposta"])
    if resultado["fallback"]:
        print(f"\nFallback: {resultado['motivo']}")
    for fonte in resultado["fontes"]:
        paginas = sorted(set([fonte["pagina"], *fonte.get("paginas_mescladas", [])]))
        print(f"[{fonte['referencia']}] {fonte['arquivo']} | "
              f"página(s): {', '.join(map(str, paginas))} | "
              f"assunto: {fonte.get('assunto')} | aula: {fonte.get('aula')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erro:
        # Mensagens externas podem carregar credenciais; não imprime traceback,
        # configuração de conexão, cabeçalhos nem a mensagem original do erro.
        print(f"Não foi possível concluir ({type(erro).__name__}). "
              "Confira a configuração local do banco e do OpenRouter.", file=sys.stderr)
        sys.exit(1)
