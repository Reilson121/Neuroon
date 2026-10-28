"""Variantes de número dos termos de ED para a busca lexical.

A pergunta e seu embedding permanecem originais. Esta expansão não fornece
respostas ao modelo nem altera o corpus, os assuntos ou suas permissões.
"""
from app.rag.hybrid_search import termos

VARIANTES = (
    ('pilha', 'pilhas'), ('fila', 'filas'), ('lista', 'listas'),
    ('ponteiro', 'ponteiros'), ('struct', 'structs'), ('arvore', 'arvores'),
    ('heap', 'heaps'), ('grafo', 'grafos'), ('rotacao', 'rotacoes'),
)


def expandir_variantes(pergunta):
    palavras = set(termos(pergunta))
    extras = []
    for variantes in VARIANTES:
        if palavras.intersection(variantes):
            extras.extend(v for v in variantes if v not in palavras)
    return ' '.join([pergunta, *extras])
