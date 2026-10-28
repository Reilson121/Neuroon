"""Validação real de busca e, com --respostas, de respostas via OpenRouter."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

from app.rag.design_corpus import DISCIPLINA, RAIZ, carregar_validado


# Evidências esperadas nas fontes, definidas antes de executar a busca.
CASOS = [
    ("artefato", "O que é um artefato digital?", "01", [18, 19, 20], None),
    ("feedback", "O que é feedback em uma interface?", "01", [38], None),
    ("bitmap_vetor", "Qual é a diferença entre imagem vetorial e bitmap?", "02", [17, 19, 20], None),
    ("persona", "Qual é a diferença entre público-alvo e persona?", "03", [8, 9, 10, 12, 17], None),
    ("consumidor", "Quais fatores influenciam o comportamento do consumidor?", "04", [3], None),
    ("arquitetura", "Quais são os sistemas da arquitetura da informação?", "05", [7, 8, 9, 10], None),
    ("gestalt", "Quais são os princípios da Gestalt?", "05", [24], None),
    ("fechamento", "O que é fechamento na Gestalt?", "05", [38], None),
    ("serifa", "Qual a diferença entre fontes com serifa e sem serifa?", "06", [24, 25, 26, 27, 28], None),
    ("familia", "O que é uma família tipográfica?", "06", [18], None),
    ("diagramacao", "Quais são os quatro princípios essenciais da diagramação?", "07", [15], None),
    ("monocromatica", "O que é harmonia monocromática?", "07", [24], None),
    ("complementar", "O que é harmonia complementar?", "07", [28, 29], None),
    ("triadica", "O que é harmonia triádica?", "07", [31], None),
    ("etapas", "Quais são as cinco etapas do Design Thinking?", "08", [10, 13, 14, 15, 16, 17], None),
    ("empatia", "Quais perguntas fazem parte do mapa de empatia?", "08", list(range(24, 32)), None),
    ("csd", "Qual a diferença entre certezas, suposições e dúvidas na matriz CSD?", "complementar", [1, 2, 5, 6, 15, 22, 25], None),
    ("csd_linhas", "Como organizar a matriz CSD em linhas por grupos de usuários?", "complementar", [26], "matriz_csd"),
    ("fora_disciplina", "Qual é a capital da França?", None, [], None),
]


def main(argv=None, *, retriever=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--respostas", action="store_true", help="Envia perguntas e trechos ao OpenRouter configurado.")
    parser.add_argument("--casos", nargs="+", choices=[c[0] for c in CASOS])
    args = parser.parse_args(argv)
    from app.rag.index_audit import auditar_indice
    from app.rag.retriever import Retriever
    from app.rag.vector_store import VectorStore
    dados = carregar_validado()
    store = VectorStore() if retriever is None else retriever.store
    auditoria = auditar_indice(store, dados["chunks"], DISCIPLINA)
    if not auditoria["compativel"]:
        print("Índice divergente. Execute scripts.indexar_design antes de validar.")
        return 2
    retriever = Retriever(store=store) if retriever is None else retriever
    origem = {c["chunk_id"]: c for c in dados["chunks"]}
    relatorio = {
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "disciplina": DISCIPLINA, "modo": "respostas" if args.respostas else "busca",
        "perfil_recuperacao": "hibrida_bm25_rrf_v2",
        "corpus_sha256": hashlib.sha256(json.dumps(dados, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "top_k": 5, "similaridade_minima": 0.25, "casos": [],
        "cobertura_lexical_minima": 0.5,
    }
    selecionados = [c for c in CASOS if not args.casos or c[0] in args.casos]
    nome = "validacao_respostas_design.json" if args.respostas else "validacao_busca_design.json"
    if args.casos:
        nome = nome.replace(".json", "_selecionados.json")
    destino = RAIZ / "saidas_testes" / nome
    for identificador, pergunta, aula, paginas, filtro in selecionados:
        print(f"Validando {identificador}: {pergunta}", flush=True)
        caso = {"id": identificador, "pergunta": pergunta, "filtro_assunto": filtro,
                "aula_esperada": aula, "paginas_esperadas": paginas}
        try:
            contexto = retriever.recuperar(pergunta, DISCIPLINA, filtro, k=5)
            valido = all(c["chunk_id"] in origem and c["conteudo"] == origem[c["chunk_id"]]["conteudo"]
                         and all(c["metadata"].get(k) == origem[c["chunk_id"]]["metadata"].get(k)
                                 for k in ("disciplina", "assunto", "aula", "arquivo", "pagina"))
                         and (filtro is None or c["metadata"]["assunto"] == filtro) for c in contexto)
            evidencia = any(c["metadata"].get("aula") == aula and c["metadata"].get("pagina") in paginas
                            for c in contexto)
            caso.update(contexto_recuperado=contexto, fontes_conferidas=valido, evidencia_no_top5=evidencia)
            if args.respostas:
                from app.rag.monitor_virtual import MonitorVirtual, PROMPT_SISTEMA
                tentativas = []

                def gerar(prompt):
                    bruto = MonitorVirtual._gerar_openrouter(prompt)
                    tentativas.append({"mensagem_pergunta_e_contexto": prompt.to_messages()[-1].content,
                                       "saida_modelo": bruto})
                    return bruto

                resultado = MonitorVirtual(retriever, gerar=gerar).responder(pergunta, DISCIPLINA, filtro)
                fontes_ok = all(f["chunk_id"] in origem and all(
                    f.get(k) == origem[f["chunk_id"]]["metadata"].get(k)
                    for k in ("arquivo", "pagina", "aula", "assunto", "disciplina")
                ) for f in resultado["fontes"])
                evidencia_citada = any(f.get("aula") == aula and f.get("pagina") in paginas
                                       for f in resultado["fontes"])
                passou = fontes_ok and (
                    resultado["fallback"] and not resultado["fontes"]
                    and resultado["motivo"] in {"sem_contexto", "contexto_insuficiente"}
                    if aula is None else not resultado["fallback"] and evidencia_citada)
                caso.update(resultado=resultado, tentativas=tentativas,
                            prompt_sha256=hashlib.sha256(PROMPT_SISTEMA.encode()).hexdigest(),
                            trechos_citados=[{"referencia": f["referencia"], "conteudo": origem[f["chunk_id"]]["conteudo"]}
                                            for f in resultado["fontes"] if f["chunk_id"] in origem],
                            evidencia_citada=evidencia_citada, revisao_semantica="pendente")
                passou = passou and valido
            else:
                if aula is None:
                    # Recuperação não decide suficiência semântica. Registra a
                    # amostra; a recusa só é validada no modo --respostas.
                    passou = None
                    caso["requer_validacao_resposta"] = True
                    caso["sem_contexto_acima_do_limiar"] = not any(c["similaridade"] >= 0.25 for c in contexto)
                else:
                    passou = valido and evidencia
            caso["verificacao_automatica"] = passou
        except Exception as erro:
            caso.update(verificacao_automatica=False, erro_tipo=type(erro).__name__)
        relatorio["casos"].append(caso)
        destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        status = "REGISTRADO; validar recusa em --respostas" if caso["verificacao_automatica"] is None else (
            "OK" if caso["verificacao_automatica"] else "REVISAR")
        print(f"Resultado: {status}", flush=True)
    print(f"Relatório salvo: {destino}", flush=True)
    return 0 if all(c["verificacao_automatica"] is not False for c in relatorio["casos"]) else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Validação não concluída ({type(erro).__name__}).", file=sys.stderr)
        sys.exit(1)
