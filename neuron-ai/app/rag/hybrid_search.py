"""Fusão de busca semântica e termos literais para os corpora locais."""

import math
import re
import unicodedata
from collections import Counter


STOPWORDS = set("""a as ao aos aquela aquele aquelas aqueles algo ante apos ate com como
da das de dela delas dele deles dentro desde desse desta desses destas do dos e ela elas
ele eles em entre era eram essa esse essas esses esta estar estas este estes eu foi foram
ha isso isto ja la lhe lhes mais mas me mesmo meu meus minha minhas muito na nas nao nem
no nos nossa nossas nosso nossos num numa o os ou para pela pelas pelo pelos por porque
qual quais quando quanto quantos que quem sao se sem seu seus sua suas ser sera sobre so
tambem te tem ter tua tuas um uma umas uns voce voces explique diferenca quais""".split())


def termos(texto):
    normal = unicodedata.normalize("NFKD", texto.casefold())
    normal = "".join(c for c in normal if not unicodedata.combining(c))
    palavras = re.findall(r"[a-z0-9]+", normal)
    # Mantém siglas (AI, UX) e elimina apenas palavras funcionais frequentes.
    return [p for p in palavras if len(p) > 1 and p not in STOPWORDS]


def ordenar_hibrido(linhas, pergunta, k):
    """BM25 + reciprocal rank fusion; preserva o cosseno original de cada linha."""
    if not linhas:
        return []
    consulta = set(termos(pergunta))
    # O assunto da aula contextualiza slides que dizem apenas "esses fatores"
    # ou apresentam uma lista, sem repetir o título da disciplina no corpo.
    contagens = [Counter(termos(linha["conteudo"] + "\n" + (linha.get("assunto") or "").replace("_", " ")))
                 for linha in linhas]
    tamanhos = [sum(c.values()) for c in contagens]
    media = sum(tamanhos) / len(tamanhos) or 1
    frequencias = Counter(t for c in contagens for t in consulta if t in c)
    idfs = {t: math.log(1 + (len(linhas) - frequencias[t] + 0.5) / (frequencias[t] + 0.5))
            for t in consulta if frequencias[t]}
    scores = []
    for contagem, tamanho in zip(contagens, tamanhos):
        score = 0.0
        for termo in consulta:
            tf = contagem[termo]
            if tf:
                idf = idfs[termo]
                score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * tamanho / media))
        scores.append(score)
    semantica = sorted(range(len(linhas)), key=lambda i: (-linhas[i]["similaridade"], linhas[i]["chunk_id"]))
    lexical = sorted((i for i in range(len(linhas)) if scores[i] > 0),
                     key=lambda i: (-scores[i], linhas[i]["chunk_id"]))
    if not lexical:
        return [linhas[i] for i in semantica[:k]]
    limite = max(20, k * 4)
    fusao = Counter()
    for peso, ranking in ((1.0, semantica), (1.5, lexical)):
        for posicao, indice in enumerate(ranking[:limite], start=1):
            fusao[indice] += peso / (60 + posicao)
    ordem = sorted(fusao, key=lambda i: (-fusao[i], -linhas[i]["similaridade"], linhas[i]["chunk_id"]))
    escolhidos, conjuntos = [], []
    for indice in ordem:
        palavras = set(termos(linhas[indice]["conteudo"]))
        # PDFs de apresentações repetem a mesma tabela em várias etapas.
        # Evita gastar todo o contexto com versões do mesmo modelo vazio.
        repetido = any(min(len(palavras), len(anterior)) >= 6 and
                       len(palavras & anterior) / min(len(palavras), len(anterior)) >= .88
                       for anterior in conjuntos)
        if repetido:
            continue
        total_idf = sum(idfs.values())
        cobertura = sum(idfs[t] for t in idfs if t in contagens[indice]) / total_idf if total_idf else 0
        escolhidos.append({**linhas[indice], "cobertura_lexical": cobertura})
        conjuntos.append(palavras)
        if len(escolhidos) == k:
            break
    return escolhidos
