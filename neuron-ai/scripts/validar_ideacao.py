"""Valida busca real; --respostas envia perguntas e trechos ao OpenRouter."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
import unicodedata

from app.rag.ideacao_corpus import DISCIPLINA, RAIZ, carregar_validado, salvar_json

# Páginas identificadas no material antes de executar a recuperação.
CASOS = [
    ("problema_solucao", "Qual é a diferença entre ideia, problema e solução?", "01", [9, 10, 11, 12, 13, 14], None),
    ("concepcao", "Quais são os três pilares da concepção de produto?", "01", [26], None),
    ("ucd", "Quais são as etapas do Design Centrado no Usuário?", "01", [31, 32], None),
    ("persona_empatia", "Qual é a diferença entre persona e mapa de empatia?", "01", [39, 46, 47, 48, 49], "introducao"),
    ("brainstorming", "Quais são os princípios fundamentais do brainstorming?", "01", [58, 59, 60], None),
    ("scamper", "Quais ações compõem a técnica SCAMPER?", "01", [67], "introducao"),
    ("lean_blocos", "Quais são os nove blocos do Lean Canvas?", "02", [8, 9], None),
    ("proposta_valor", "Como estruturar a proposta única de valor no Lean Canvas?", "02", [15, 16, 17], None),
    ("metricas", "Qual é a diferença entre métricas de vaidade e métricas relevantes?", "02", [27], None),
    ("hipoteses", "Como validar as hipóteses do Lean Canvas?", "02", [31, 32, 33], "lean_canvas"),
    ("historia_estrutura", "Qual é a estrutura básica de uma história de usuário?", "03", [3, 5, 6, 7, 8, 11], None),
    ("historia_boas_praticas", "Como criar boas histórias de usuário?", "03", [9, 10], "historias_de_usuario"),
    ("mapa_fluxo", "Qual é a diferença entre mapa de navegação e fluxo do usuário?", "04", [11, 12], None),
    ("hierarquia", "Como funciona a estrutura hierárquica de navegação?", "04", [7], "mapa_de_navegacao_e_wireframe"),
    ("wireframe", "O que é um wireframe e qual é sua finalidade?", "04", [17, 18, 19, 20], None),
    ("fidelidade", "Quais são os níveis de fidelidade de um wireframe?", "04", [22, 23, 24, 25], None),
    ("mockup_prototipo", "Qual é a diferença entre wireframe, mockup e protótipo?", "04", [26], None),
    ("estados_interface", "Quais estados da interface podem ser representados em um wireframe?", "04", [33], "mapa_de_navegacao_e_wireframe"),
    ("csd", "Qual é a diferença entre certezas, suposições e dúvidas na matriz CSD?", "05", [3, 5, 6, 8, 10, 11], None),
    ("certeza_fonte", "Como escrever uma certeza na matriz CSD?", "05", [6, 7], "matriz_csd"),
    ("priorizar", "O que investigar primeiro na matriz CSD?", "05", [17], "matriz_csd"),
    ("atualizar_csd", "Como atualizar a matriz CSD depois de uma investigação?", "05", [18], "matriz_csd"),
    ("fora_disciplina", "Qual é a capital da França?", None, [], None),
]


# Critérios de completude derivados das listas explícitas dos slides.
# Cada grupo admite variantes linguísticas para o mesmo conceito.
CONCEITOS = {
    "concepcao": [("usuario",), ("negocio",), ("tecnologia",)],
    "ucd": [("compreender",), ("definir",), ("prototipar",), ("testar",), ("refinar",), ("implementar",)],
    "brainstorming": [("quantidade",), ("julgamento",), ("criatividade",), ("liberdade",)],
    "scamper": [("substituir",), ("combinar",), ("adaptar",), ("modificar",),
                ("outro uso", "outro proposito"), ("eliminar",), ("reverter",)],
    "lean_blocos": [("problema",), ("segmento",), ("proposta",), ("solucao",),
                    ("canais",), ("receita",), ("custo",), ("metricas",), ("vantagem",)],
    "historia_estrutura": [("usuario",), ("quero",), ("para",)],
    "fidelidade": [("baixa",), ("media",), ("alta",)],
    "mockup_prototipo": [("wireframe",), ("mockup",), ("prototipo",)],
    "estados_interface": [("inicial",), ("carregamento",), ("ausencia", "vazio"),
                          ("sucesso",), ("erro",), ("obrigatorio",), ("conexao",),
                          ("busca",), ("confirmacao",)],
    "csd": [("certeza",), ("supos",), ("duvida",)],
    "priorizar": [("impacto",), ("incerteza",), ("dependencia",), ("esforco",)],
}


def conceitos_ausentes(identificador, resposta):
    normal = unicodedata.normalize("NFKD", resposta.casefold())
    normal = "".join(c for c in normal if not unicodedata.combining(c))
    return [grupo[0] for grupo in CONCEITOS.get(identificador, [])
            if not any(termo in normal for termo in grupo)]


def contexto_util(trecho):
    return trecho["similaridade"] >= 0.25 or trecho.get("cobertura_lexical", 0) >= 0.5


def conferir_fontes(itens, origem, filtro=None, trechos=False):
    for item in itens:
        chunk = origem.get(item["chunk_id"])
        if chunk is None:
            return False
        metadata = item["metadata"] if trechos else item
        if any(metadata.get(k) != chunk["metadata"].get(k)
               for k in ("disciplina", "assunto", "aula", "arquivo", "pagina", "periodo")):
            return False
        if filtro is not None and metadata.get("assunto") != filtro:
            return False
        if trechos and item["conteudo"] != chunk["conteudo"]:
            return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--respostas", action="store_true")
    parser.add_argument("--http", action="store_true", help="Valida respostas pela rota interna FastAPI.")
    parser.add_argument("--casos", nargs="+", choices=[c[0] for c in CASOS])
    args = parser.parse_args(argv)
    if args.http and not args.respostas:
        parser.error("--http exige --respostas")
    from app.rag.index_audit import auditar_indice
    from app.rag.retriever import Retriever
    from app.rag.vector_store import VectorStore
    dados = carregar_validado()
    store = VectorStore()
    auditoria = auditar_indice(store, dados["chunks"], DISCIPLINA)
    if not auditoria["compativel"]:
        print("Índice divergente. Execute scripts.indexar_ideacao.")
        return 2
    retriever = Retriever(store=store)
    origem = {c["chunk_id"]: c for c in dados["chunks"]}
    relatorio = {
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "disciplina": DISCIPLINA, "modo": "respostas" if args.respostas else "busca",
        "transporte": "http_fastapi_testclient" if args.http else "direto",
        "corpus_sha256": hashlib.sha256(json.dumps(dados, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "top_k": 5, "similaridade_minima": 0.25, "auditoria": auditoria, "casos": [],
    }
    nome = "validacao_respostas_ideacao.json" if args.respostas else "validacao_busca_ideacao.json"
    if args.http:
        nome = nome.replace(".json", "_http.json")
    if args.casos:
        nome = nome.replace(".json", "_selecionados.json")
    destino = RAIZ / "saidas_testes" / nome
    for identificador, pergunta, aula, paginas, filtro in CASOS:
        if args.casos and identificador not in args.casos:
            continue
        print(f"Validando {identificador}...", flush=True)
        caso = {"id": identificador, "pergunta": pergunta, "filtro_assunto": filtro,
                "aula_esperada": aula, "paginas_esperadas": paginas}
        try:
            contexto = retriever.recuperar(pergunta, DISCIPLINA, filtro, k=5)
            valido = conferir_fontes(contexto, origem, filtro, trechos=True)
            evidencia = any(c["metadata"].get("aula") == aula and c["metadata"].get("pagina") in paginas
                            and contexto_util(c) for c in contexto)
            caso.update(contexto_recuperado=contexto, fontes_conferidas=valido, evidencia_no_top5=evidencia)
            if args.respostas:
                from app.rag.monitor_virtual import MonitorVirtual, PROMPT_SISTEMA
                tentativas = []

                def gerar(prompt):
                    bruto = MonitorVirtual._gerar_openrouter(prompt)
                    tentativas.append({"mensagem_pergunta_e_contexto": prompt.to_messages()[-1].content,
                                       "saida_modelo": bruto})
                    return bruto

                monitor = MonitorVirtual(retriever, gerar=gerar)
                if args.http:
                    from unittest.mock import patch
                    from fastapi.testclient import TestClient
                    from app.main import app
                    with patch("app.api.chat.obter_monitor", return_value=monitor), TestClient(app) as cliente:
                        resposta = cliente.post("/internal/v1/chat", json={
                            "pergunta": pergunta, "disciplina": DISCIPLINA, "assunto": filtro})
                        caso["http_status"] = resposta.status_code
                        if resposta.status_code != 200:
                            raise RuntimeError("Falha HTTP na validação.")
                        resultado = resposta.json()
                else:
                    resultado = monitor.responder(pergunta, DISCIPLINA, filtro)
                fontes_ok = conferir_fontes(resultado["fontes"], origem, filtro)
                evidencia_citada = any(f.get("aula") == aula and f.get("pagina") in paginas
                                       for f in resultado["fontes"])
                if aula is None:
                    passou = (resultado["fallback"] and not resultado["fontes"]
                              and resultado["motivo"] in {"sem_contexto", "contexto_insuficiente"})
                else:
                    passou = not resultado["fallback"] and evidencia_citada
                passou = passou and fontes_ok and valido
                ausentes = conceitos_ausentes(identificador, resultado["resposta"]) if aula is not None else []
                passou = passou and not ausentes
                caso.update(resultado=resultado, tentativas=tentativas,
                            conceitos_ausentes=ausentes,
                            prompt_sha256=hashlib.sha256(PROMPT_SISTEMA.encode()).hexdigest(),
                            trechos_citados=[{"referencia": f["referencia"], "conteudo": origem[f["chunk_id"]]["conteudo"]}
                                            for f in resultado["fontes"] if f["chunk_id"] in origem],
                            evidencia_citada=evidencia_citada, revisao_semantica="pendente")
            else:
                passou = valido and (evidencia if aula is not None else not any(contexto_util(c) for c in contexto))
            caso["verificacao_automatica"] = passou
        except Exception as erro:
            caso.update(verificacao_automatica=False, erro_tipo=type(erro).__name__)
        relatorio["casos"].append(caso)
        salvar_json(destino, relatorio)
        print(f"Resultado: {'OK' if caso['verificacao_automatica'] else 'REVISAR'}", flush=True)
    print(f"Relatório salvo: {destino}", flush=True)
    return 0 if all(c["verificacao_automatica"] for c in relatorio["casos"]) else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Validação não concluída ({type(erro).__name__}).", file=sys.stderr)
        sys.exit(1)
