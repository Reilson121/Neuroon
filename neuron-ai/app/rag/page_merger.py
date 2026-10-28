"""
Junção de páginas curtas (só título ou chamada) com a página seguinte.

Slides como "Árvore Trie" ou "VAMOS REVISAR?" viram chunks quase vazios
que ganham o ranking da busca (o título casa com a pergunta) mas não
explicam nada. Aqui, cada página textual curta é colocada no início da
próxima página do MESMO assunto, que passa a ter título + conteúdo.

Regras:
- só páginas textuais com menos de MINIMO_CARACTERES caracteres;
- nunca junta páginas de assuntos diferentes;
- uma sequência de páginas curtas é toda levada para a próxima página;
- se não houver próxima página no mesmo assunto, a página curta fica
  como está (nada é descartado);
- o texto curto não é duplicado se a próxima página já o contém no início;
- a página que recebe o texto mantém seu número (e seu chunk_id) e ganha
  metadata["paginas_mescladas"] com os números das páginas absorvidas.
"""

MINIMO_CARACTERES = 60


def _curta(pagina, minimo):
    return (
        pagina["metadata"]["tipo_extracao"] == "textual"
        and len(pagina["conteudo"].strip()) < minimo
    )


def mesclar_paginas_curtas(paginas, minimo=MINIMO_CARACTERES):
    """
    Recebe as páginas de UM arquivo, em ordem.
    Retorna (paginas_resultantes, quantidade_de_paginas_absorvidas).
    """
    resultado = []
    pendentes = []
    absorvidas = 0

    for pagina in paginas:

        # Mudou de assunto: as pendentes não têm para onde ir.
        if (
            pendentes
            and pendentes[0]["metadata"]["assunto"]
            != pagina["metadata"]["assunto"]
        ):
            resultado.extend(pendentes)
            pendentes = []

        if _curta(pagina, minimo):
            pendentes.append(pagina)
            continue

        if pendentes:
            inicio = " ".join(pagina["conteudo"][:300].split())
            textos = []

            for curta in pendentes:
                texto = curta["conteudo"].strip()
                if " ".join(texto.split()) not in inicio:
                    textos.append(texto)

            pagina["conteudo"] = "\n".join(
                textos + [pagina["conteudo"]]
            )

            pagina["metadata"]["paginas_mescladas"] = [
                p["metadata"]["pagina"] for p in pendentes
            ]
            pagina["metadata"]["motivos_deteccao"].append(
                "paginas_curtas_mescladas"
            )

            absorvidas += len(pendentes)
            pendentes = []

        resultado.append(pagina)

    resultado.extend(pendentes)

    return resultado, absorvidas
