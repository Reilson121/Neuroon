"""Equivalências explícitas no material de Ideação, apenas para busca lexical."""

import re
import unicodedata
import math
from collections import Counter


def expandir_siglas(pergunta):
    # A aula 01, p. 27, apresenta "Design Centrado no Usuário (UCD)";
    # a continuação nas páginas 31 e 32 utiliza somente a sigla.
    normal = unicodedata.normalize("NFKD", pergunta.casefold())
    normal = "".join(c for c in normal if not unicodedata.combining(c))
    if "design centrado no usuario" in normal or re.search(r"\bucd\b", normal):
        # O embedding mantém a pergunta completa. A âncora literal evita que
        # "design", "usuário" e "etapas" promovam slides de Design Thinking.
        return "UCD"
    if "proposta unica de valor" in normal or re.search(r"\bpuv\b", normal):
        # As páginas 15-17 da aula 02 alternam o título completo e a forma
        # "proposta de valor"; "Lean Canvas" aparece em muitos slides gerais.
        return "proposta valor"
    return pergunta


def ordenar_evidencias(linhas, pergunta, k):
    """Combina BM25 normalizado (70%) e cosseno (30%) no corpus de Ideação.

    A fusão apenas por posição pode esconder um termo raro como "vaidade"
    quando muitos slides gerais aparecem nos dois rankings.
    """
    from app.rag.hybrid_search import termos
    if not linhas:
        return []
    consulta = set(termos(expandir_siglas(pergunta)))
    contagens = [Counter(termos(linha["conteudo"] + " " +
                               (linha.get("assunto") or "").replace("_", " "))) for linha in linhas]
    tamanhos = [sum(c.values()) for c in contagens]
    media = sum(tamanhos) / len(tamanhos) or 1
    frequencias = Counter(t for c in contagens for t in consulta if t in c)
    idfs = {t: math.log(1 + (len(linhas) - frequencias[t] + .5) / (frequencias[t] + .5))
            for t in consulta if frequencias[t]}
    scores = []
    for contagem, tamanho in zip(contagens, tamanhos):
        scores.append(sum(idfs[t] * contagem[t] * 2.2 /
                          (contagem[t] + 1.2 * (.25 + .75 * tamanho / media))
                          for t in idfs if contagem[t]))
    maior = max(scores, default=0)
    if not maior:
        return sorted(linhas, key=lambda l: (-l["similaridade"], l["chunk_id"]))[:k]
    total_idf = sum(idfs.values())
    relevancias = [.7 * scores[i] / maior + .3 * linhas[i]["similaridade"] for i in range(len(linhas))]
    ordem = sorted(range(len(linhas)), key=lambda i: (-relevancias[i], linhas[i]["chunk_id"]))
    # Não preenche o contexto com slides gerais muito abaixo da melhor
    # evidência. Mantém páginas complementares com relevância semelhante.
    limite = relevancias[ordem[0]] * .65
    ordem = [i for i in ordem if relevancias[i] >= limite]
    return [{**linhas[i], "cobertura_lexical": sum(idfs[t] for t in idfs if contagens[i][t]) / total_idf}
            for i in ordem[:k]]
