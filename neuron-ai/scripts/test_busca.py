import sys

from app.rag.embedding_processor import EmbeddingProcessor
from app.rag.vector_store import VectorStore


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DISCIPLINA = "estrutura_de_dados_avancada"
K = 3

# (pergunta, filtro de assunto, assunto esperado no topo)
PERGUNTAS = [
    ("O que é uma fila de prioridade?",
     None, "filas_de_prioridade_e_heap"),
    ("Como funciona a rotação zig-zag em uma árvore AVL?",
     None, "arvores_balanceadas_e_avl"),
    ("Qual a diferença entre uma BST e um Max-Heap no HeapSort?",
     None, "algoritmos_de_ordenacao"),
    ("Como calcular o índice de Gini em uma árvore de decisão?",
     None, "arvores_de_decisao"),
    ("O que é uma árvore trie?",
     None, "arvore_trie"),
    ("Quais são as propriedades de uma árvore red-black?",
     None, "arvores_red_black"),
    ("Como funciona uma árvore splay?",
     "arvore_splay", "arvore_splay"),
    ("Qual é a capital da França?",
     None, None),
]

print("=" * 80)
print("TESTE DE BUSCA VETORIAL TOP-K")
print("=" * 80)

embedder = EmbeddingProcessor()
store = VectorStore()

acertos_top1 = 0
acertos_topk = 0
com_esperado = 0

for pergunta, filtro, esperado in PERGUNTAS:

    embedding = embedder.gerar_embedding(pergunta)

    resultados = store.buscar_similares(
        embedding,
        DISCIPLINA,
        assunto=filtro,
        k=K
    )

    print("\n" + "-" * 80)
    print(f"PERGUNTA: {pergunta}")
    print(f"Filtro de assunto: {filtro or '(nenhum)'}"
          f" | Esperado no topo: {esperado or '(fora do escopo)'}")

    for posicao, r in enumerate(resultados, start=1):
        previa = " ".join(r["conteudo"].split())[:110]
        print(
            f"  {posicao}. sim={r['similaridade']:.3f} | "
            f"{r['assunto']} | {r['arquivo']} p.{r['pagina']}"
        )
        print(f"     {previa}")

    if esperado:
        com_esperado += 1
        assuntos = [r["assunto"] for r in resultados]

        if assuntos and assuntos[0] == esperado:
            acertos_top1 += 1
            print("  -> TOPO CORRETO")
        elif esperado in assuntos:
            acertos_topk += 1
            print(f"  -> esperado aparece no top-{K}, mas nao em 1o")
        else:
            print("  -> DIVERGENTE: esperado nao apareceu")

print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)
print(f"Perguntas com assunto esperado: {com_esperado}")
print(f"Top-1 correto: {acertos_top1}")
print(f"Esperado so no top-{K}: {acertos_topk}")
