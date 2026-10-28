"""Valida respostas reais dos seis temas adicionais; não escreve no banco."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

from scripts.monitor_ed_avancada import DISCIPLINA, JSON_CHUNKS, RAIZ


CASOS = [
    ("Como funciona a rotação zig-zag em uma árvore AVL?", None, "arvores_balanceadas_e_avl"),
    ("Qual a diferença entre uma BST e um Max-Heap no HeapSort?", None, "algoritmos_de_ordenacao"),
    ("Como calcular o índice de Gini em uma árvore de decisão?", None, "arvores_de_decisao"),
    ("O que é uma árvore trie?", None, "arvore_trie"),
    ("Quais são as propriedades de uma árvore red-black?", None, "arvores_red_black"),
    ("Como funciona uma árvore splay?", "arvore_splay", "arvore_splay"),
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from app.rag.index_audit import auditar_indice
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revisar-pendentes", action="store_true")
    args = parser.parse_args()
    from app.rag.monitor_virtual import MonitorVirtual, PROMPT_SISTEMA
    from app.rag.retriever import Retriever
    from app.rag.vector_store import VectorStore

    chunks = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))["chunks"]
    origem = {c["chunk_id"]: c for c in chunks}
    store = VectorStore()
    if not auditar_indice(store, chunks, DISCIPLINA)["compativel"]:
        print("O índice precisa ser sincronizado antes da validação.", flush=True)
        return 2
    monitor = MonitorVirtual(Retriever(store=store))
    destino = RAIZ / "saidas_testes/validacao_respostas_ed_avancada.json"
    anterior = json.loads(destino.read_text(encoding="utf-8")) if args.revisar_pendentes else {}
    pendentes = {c["pergunta"] for c in anterior.get("casos", []) if not c["verificacao_automatica"]}
    casos = [c for c in CASOS if not args.revisar_pendentes or c[0] in pendentes]
    relatorio = {
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "disciplina": DISCIPLINA, "chunks": len(chunks),
        "top_k": monitor.k, "similaridade_minima_experimental": monitor.similaridade_minima,
        "casos": anterior.get("casos", []),
    }
    for pergunta, assunto, esperado in casos:
        print(f"Validando: {pergunta}", flush=True)
        captura = {}

        def gerar(prompt):
            # O contexto contém somente os trechos acadêmicos enviados ao LLM.
            captura["contexto_recuperado"] = json.loads(
                prompt.to_messages()[-1].content.split("\n\nCONTEXTO (JSON):\n", 1)[1]
            )
            bruto = MonitorVirtual._gerar_openrouter(prompt)
            captura["saida_modelo"] = bruto
            captura.setdefault("tentativas", []).append({
                "mensagem_pergunta_e_contexto": prompt.to_messages()[-1].content,
                "saida_modelo": bruto,
            })
            return bruto

        # Reutiliza o mesmo embedder e registra o texto acadêmico retornado pelo LLM.
        atual = MonitorVirtual(monitor.retriever, gerar=gerar)
        try:
            resultado = atual.responder(pergunta, DISCIPLINA, assunto)
            fontes_validas = bool(resultado["fontes"]) and all(
                fonte["chunk_id"] in origem
                and all(
                    fonte.get(campo) == origem[fonte["chunk_id"]]["metadata"].get(campo)
                    for campo in ("arquivo", "pagina", "assunto", "disciplina")
                )
                for fonte in resultado["fontes"]
            )
            assunto_citado = any(f.get("assunto") == esperado for f in resultado["fontes"])
            passou = not resultado["fallback"] and fontes_validas and assunto_citado
            caso = {
                "pergunta": pergunta, "filtro_assunto": assunto,
                "prompt_sha256": hashlib.sha256(PROMPT_SISTEMA.encode()).hexdigest(),
                "verificacao_automatica": passou,
                "revisao_semantica": "pendente",
                **resultado, **captura,
                "trechos_citados": [
                    {"referencia": f["referencia"],
                     "conteudo": origem[f["chunk_id"]]["conteudo"]}
                    for f in resultado["fontes"] if f["chunk_id"] in origem
                ],
            }
            if resultado["motivo"] == "contexto_insuficiente":
                # Diagnóstico, sem mudar Top-K do fluxo nem gerar outra resposta.
                amostra = monitor.retriever.recuperar(pergunta, DISCIPLINA, assunto, k=10)
                caso["diagnostico_top10"] = [
                    {"pagina": c["metadata"]["pagina"],
                     "assunto": c["metadata"]["assunto"],
                     "similaridade": c["similaridade"]}
                    for c in amostra
                ]
            print(f"Resultado: {'OK' if passou else 'REVISAR'} | "
                  f"fontes={len(resultado['fontes'])} | motivo={resultado['motivo']}", flush=True)
        except Exception as erro:
            caso = {"pergunta": pergunta, "verificacao_automatica": False,
                    "erro_tipo": type(erro).__name__, "revisao_semantica": "pendente"}
            print(f"Resultado: ERRO ({type(erro).__name__})", flush=True)
        anteriores = [c for c in relatorio["casos"] if c["pergunta"] == pergunta]
        if anteriores:
            caso["historico"] = anteriores[0].get("historico", []) + [
                {k: v for k, v in anteriores[0].items() if k != "historico"}
            ]
        relatorio["casos"] = [c for c in relatorio["casos"] if c["pergunta"] != pergunta] + [caso]
        destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Relatório salvo: {destino}", flush=True)
    return 0 if all(c["verificacao_automatica"] for c in relatorio["casos"]) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Validação interrompida ({type(erro).__name__}).", file=sys.stderr)
        sys.exit(1)
