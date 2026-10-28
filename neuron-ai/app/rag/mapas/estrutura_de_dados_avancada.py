"""
Mapa de assuntos da disciplina Estrutura de Dados Avançada (3º período).

Cada PDF tem vários assuntos. Aqui dizemos, para cada arquivo, em quais
PÁGINAS cada assunto está (faixas incluem inicial e final).

- Páginas fora de qualquer assunto (capa, página em branco) não entram
  no RAG e nunca chamam a API.
- "paginas_textuais": força extração textual (ex.: páginas só com título).
- "paginas_multimodais": força análise visual (tabela/árvore em imagem).

Rascunho baseado nos títulos das páginas. Revisar com a ementa.
"""

MAPA = {
    "periodo": "03",
    "disciplina": "estrutura_de_dados_avancada",
    "arquivos": {
        "Aula_0.pdf": {
            "aula": "00",
            "assuntos": {
                "apresentacao_e_ementa": [(2, 3)],
                "revisao_estruturas_em_c": [(4, 14)],
                "conceitos_de_arvores": [(15, 28)],
            },
            "paginas_textuais": [2, 4, 15, 19, 23, 25],
            "paginas_multimodais": [],
        },
        "Aula_1.pdf": {
            "aula": "01",
            "assuntos": {
                "arvores_em_python": [(3, 19)],
                "aplicacoes_de_arvores": [(20, 35)],
            },
            "paginas_textuais": [19, 21, 22, 24, 26, 28],
            "paginas_multimodais": [],
        },
        "Aula_2.pdf": {
            "aula": "02",
            "assuntos": {
                "filas_de_prioridade_e_heap": [(3, 9)],
                "arvores_binarias_de_busca": [(10, 15), (81, 82)],
                "arvores_de_decisao": [(16, 73)],
                "arvore_trie": [(74, 80)],
                "arvores_balanceadas_e_avl": [(83, 94)],
                "arvores_red_black": [(95, 103)],
                "arvore_splay": [(104, 108)],
                "algoritmos_de_ordenacao": [(109, 127)],
                "grafos": [(129, 130), (132, 144)],
            },
            "paginas_textuais": [27, 33, 43, 49, 56, 74, 81, 129],
            "paginas_multimodais": [58, 90, 91, 113],
        },
    },
}

