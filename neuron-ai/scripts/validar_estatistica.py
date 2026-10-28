"""Confere busca real e, com --respostas, respostas pelo Monitor existente.

As páginas esperadas foram identificadas no inventário, antes da busca.
O relatório distingue integridade automática de revisão semântica humana.
"""

import argparse
import json
import sys
from datetime import datetime, timezone

from app.rag.estatistica_corpus import DISCIPLINA, JSON_CHUNKS, RAIZ, carregar_validado, salvar_json, sha256

CASOS = [
    ("fundamentos", "O que é o espaço amostral de um experimento?", "fundamentos_de_probabilidade", [4]),
    ("arranjos", "Como calcular arranjos de k elementos distintos escolhidos entre n elementos?", "analise_combinatoria", [13, 14]),
    ("condicional", "Qual é a fórmula de probabilidade condicional P(A|B)?", "probabilidade_condicional_e_independencia", [10, 11]),
    ("tipos_dados", "Qual é a diferença entre dados quantitativos e qualitativos?", "introducao_estatistica_e_tipos_de_dados", [23, 24]),
    ("massa_densidade", "Qual é a diferença entre função massa e função densidade de probabilidade?", "variaveis_aleatorias_e_distribuicoes", [26, 27, 28]),
    ("mediana", "O que representa a mediana e como os valores extremos afetam a escolha da medida central?", "medidas_de_tendencia_central", [31, 32, 35]),
    ("quartis", "Como calcular quartis e o intervalo interquartil pelo índice iniciado em zero?", "medidas_de_dispersao_e_posicao", [40]),
    ("esperanca", "Como se calcula o valor esperado de uma variável aleatória discreta?", "valor_esperado_e_momentos", [42, 109]),
    ("correlacao", "Como interpretar os valores do coeficiente de correlação?", "correlacao_e_associacao", [44, 45, 61]),
    ("frequencias", "Na tabela de frequências do exemplo, quais são a frequência relativa e a acumulada da classe 31 a 42?", "distribuicoes_de_frequencia", [51]),
    ("histograma", "No histograma de uso da internet, qual intervalo tem frequência 13?", "representacoes_graficas", [53]),
    ("amostragem", "Quais são os métodos de amostragem apresentados no material?", "planejamento_e_amostragem", [69, 70, 73]),
    ("bootstrap", "O que é bootstrap e qual é a finalidade da reamostragem?", "reamostragem_e_bootstrap", [74]),
    ("erro_padrao", "Qual é a fórmula do erro padrão da média em função de sigma e n?", "estimacao_e_intervalos_para_media", [77, 82, 83, 84]),
    ("student", "Quais são os graus de liberdade ao estimar uma média usando a distribuição t?", "distribuicao_t_e_intervalos_para_media", [89, 92]),
    ("proporcao", "Como se calcula a estimativa pontual de uma proporção populacional?", "estimacao_e_intervalos_para_proporcoes", [95, 96, 98]),
    ("ic_variancia", "Como construir um intervalo de confiança para variância populacional com qui-quadrado?", "qui_quadrado_e_intervalos_para_variancia", [100, 101, 104, 105]),
    ("binomial", "Qual é a fórmula da probabilidade de exatamente x sucessos em n tentativas binomiais?", "distribuicao_binomial", [112]),
    ("geometrica", "Quando uma variável aleatória segue distribuição geométrica?", "distribuicao_geometrica", [114]),
    ("poisson", "Quais condições caracterizam a distribuição de Poisson?", "distribuicao_de_poisson", [115, 116]),
    ("anova", "Como a estatística F compara a variação entre os grupos e dentro dos grupos em ANOVA?", "distribuicao_f_e_anova", [117, 118, 124, 150]),
    ("caudas", "Qual é o papel do QQ-plot para identificar caudas longas ou assimetria?", "caudas_longas_e_qq_plot", [125, 127]),
    ("tcl", "O que afirma o Teorema Central do Limite sobre médias amostrais?", "distribuicao_normal_tcl_e_aproximacao_binomial", [129]),
    ("p_valor", "Como interpretar p-valor e o nível de significância em um teste?", "experimentos_e_testes_de_hipoteses", [136, 138, 139]),
    ("teste_t", "No teste t para duas amostras, qual hipótese permite usar n1+n2-2 graus de liberdade?", "testes_z_e_t", [144, 145]),
    ("independencia", "Como calcular frequências esperadas em uma tabela para o teste qui-quadrado de independência?", "teste_qui_quadrado_de_independencia", [146, 147]),
    ("permutacao", "Como é calculado o p-valor exato no exemplo das 35 permutações?", "testes_de_permutacao_e_monte_carlo", [153, 154, 155, 156]),
    ("intercepto", "Na regressão linear, o que representa o intercepto b0?", "regressao_linear_simples_e_multipla", [161, 163]),
    ("rmse", "O que mede o RMSE e qual é sua fórmula?", "avaliacao_de_regressao", [165, 166]),
    ("validacao_cruzada", "Quais são as etapas da validação cruzada K-fold?", "validacao_cruzada", [171, 172]),
    ("stepwise", "Qual é o objetivo da seleção de modelos e da regressão stepwise?", "selecao_de_modelos_e_stepwise", [175, 176]),
]


def fontes_validas(itens, origem, filtro=None, trechos=False):
    for item in itens:
        chunk = origem.get(item["chunk_id"])
        if chunk is None:
            return False
        metadata = item["metadata"] if trechos else item
        if any(metadata.get(k) != chunk["metadata"].get(k)
               for k in ("disciplina", "assunto", "arquivo", "pagina", "aula", "periodo", "paginas_mescladas")):
            return False
        if any(metadata.get(k) != v for k, v in chunk["metadata"].items()):
            return False
        if filtro is not None and metadata.get("assunto") != filtro:
            return False
        if trechos and item["conteudo"] != chunk["conteudo"]:
            return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--respostas", action="store_true")
    parser.add_argument("--casos", nargs="+", choices=[c[0] for c in CASOS])
    args = parser.parse_args(argv)
    from app.rag.index_audit import auditar_indice
    from app.rag.vector_store import VectorStore
    from app.rag.retriever import Retriever
    from app.rag.monitor_virtual import MonitorVirtual

    dados = carregar_validado()
    store = VectorStore()
    if not auditar_indice(store, dados["chunks"], DISCIPLINA, tipos_material=["SLIDE_AULA"])["compativel"]:
        raise ValueError("Índice divergente do corpus validado.")
    origem = {c["chunk_id"]: c for c in dados["chunks"]}
    retriever = Retriever(store=store)
    monitor = MonitorVirtual(retriever=retriever)
    resultados = []
    for codigo, pergunta, assunto, esperadas in CASOS:
        if args.casos and codigo not in args.casos:
            continue
        trechos = retriever.recuperar(pergunta, DISCIPLINA, assunto, k=5)
        encontradas = {n for c in trechos for n in [c["metadata"]["pagina"], *c["metadata"].get("paginas_mescladas", [])]}
        registro = {"caso": codigo, "pergunta": pergunta, "assunto": assunto, "paginas_esperadas": esperadas,
                    "pagina_relevante_recuperada": bool(encontradas & set(esperadas)),
                    "metadados_e_filtro_validos": fontes_validas(trechos, origem, assunto, trechos=True),
                    "trechos": trechos}
        registro["busca_sem_filtro"] = retriever.recuperar(pergunta, DISCIPLINA, k=5)
        registro["disciplina_preservada_sem_filtro"] = fontes_validas(registro["busca_sem_filtro"], origem, trechos=True)
        if args.respostas:
            resposta = monitor.responder(pergunta, DISCIPLINA, assunto)
            registro["resposta"] = resposta
            registro["fontes_resposta_validas"] = fontes_validas(resposta["fontes"], origem, assunto)
            registro["revisao_semantica"] = "pendente_conferencia_dos_trechos_e_resposta"
        resultados.append(registro)
        print(f"{codigo}: busca={'OK' if registro['pagina_relevante_recuperada'] and registro['metadados_e_filtro_validos'] else 'REVISAR'}", flush=True)

    vazios = []
    for disciplina, assunto in [(DISCIPLINA, "assunto_inexistente"), ("disciplina_sem_material", None)]:
        itens = retriever.recuperar("O que é probabilidade?", disciplina, assunto, k=5)
        vazios.append({"disciplina": disciplina, "assunto": assunto, "vazio": not itens})
    fora = monitor.responder("Qual é a capital da França?", DISCIPLINA) if args.respostas else None
    relatorio = {"corpus_sha256": sha256(JSON_CHUNKS.read_bytes()), "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
                 "casos": resultados, "filtros_sem_material": vazios, "fora_da_disciplina": fora}
    nome = "estatistica_validacao_respostas.json" if args.respostas else "estatistica_validacao_busca.json"
    salvar_json(RAIZ / "saidas_testes" / nome, relatorio)
    falhas = [r["caso"] for r in resultados if not r["pagina_relevante_recuperada"] or
              not r["metadados_e_filtro_validos"] or not r["disciplina_preservada_sem_filtro"]]
    if any(not v["vazio"] for v in vazios):
        falhas.append("filtros_sem_material")
    print(json.dumps({"casos": len(resultados), "falhas_estrutura_busca": falhas,
                      "revisao_semantica_pendente": args.respostas}, ensure_ascii=False))
    return 1 if falhas else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Validação interrompida ({type(erro).__name__}); confira corpus, índice e configuração.", file=sys.stderr)
        sys.exit(1)
