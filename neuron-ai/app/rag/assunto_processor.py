import json
from pathlib import Path

import pymupdf

from app.rag.document_processor import DocumentProcessor
from app.rag.chunk_processor import ChunkProcessor
from app.rag.text_cleaner import remover_repeticoes_consecutivas
from app.rag.page_merger import mesclar_paginas_curtas


class AssuntoProcessor:
    """
    Ingestão de disciplinas organizadas por ASSUNTO (e não por aula).

    Usado quando um mesmo PDF contém vários assuntos. O mapa diz em
    quais páginas cada assunto está (veja app/rag/mapas/).

    Fluxo:
        mapa -> valida -> DocumentProcessor (1x por PDF)
             -> rotula cada página com seu assunto
             -> ChunkProcessor -> chunks com metadados

    Este processador NÃO altera o DocumentProcessor, o ChunkProcessor
    nem o DisciplineProcessor (já testados): apenas os reutiliza.
    """

    def __init__(self, chunk_size=1000, chunk_overlap=150):
        self.document_processor = DocumentProcessor()
        self.chunk_processor = ChunkProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    # =========================================================
    # MAPA DE PÁGINAS
    # =========================================================

    @staticmethod
    def paginas_por_assunto(config_arquivo):
        """
        Converte as faixas do mapa em {pagina: assunto}.
        Levanta erro se duas faixas se sobrepuserem.
        """
        mapa = {}

        for assunto, faixas in config_arquivo["assuntos"].items():
            for inicio, fim in faixas:

                if inicio > fim:
                    raise ValueError(
                        f"Faixa inválida em '{assunto}': "
                        f"({inicio}, {fim})"
                    )

                for pagina in range(inicio, fim + 1):

                    if pagina in mapa:
                        raise ValueError(
                            f"Página {pagina} está em dois "
                            f"assuntos: '{mapa[pagina]}' e "
                            f"'{assunto}'."
                        )

                    mapa[pagina] = assunto

        return mapa

    def validar_arquivo(self, nome, config, total_paginas):
        """
        Confere o mapa de um arquivo contra o PDF real.
        Retorna o dicionário {pagina: assunto}.
        """
        mapa = self.paginas_por_assunto(config)

        fora = [p for p in mapa if p < 1 or p > total_paginas]
        if fora:
            raise ValueError(
                f"{nome}: páginas fora do documento "
                f"(1 a {total_paginas}): {sorted(fora)}"
            )

        textuais = set(config.get("paginas_textuais", []))
        multimodais = set(config.get("paginas_multimodais", []))

        conflito = textuais & multimodais
        if conflito:
            raise ValueError(
                f"{nome}: páginas textuais e multimodais ao mesmo "
                f"tempo: {sorted(conflito)}"
            )

        for p in multimodais:
            if p not in mapa:
                raise ValueError(
                    f"{nome}: página multimodal {p} não pertence "
                    "a nenhum assunto (não será indexada)."
                )

        return mapa

    @staticmethod
    def corrigir_repeticao(conteudo):
        """
        Protege contra sa?da "em loop" do modelo de vis?o, que ?s vezes
        repete o mesmo bloco at? estourar o limite de tokens.

        S? age quando o texto ? longo (60+ linhas) e quase todas as
        linhas s?o repetidas (menos de 30% ?nicas). Nesse caso corta o
        texto antes da segunda apari??o de um t?tulo j? visto,
        preservando o primeiro bloco (o conte?do real).

        Retorna (conteudo, foi_corrigido).
        """
        linhas = conteudo.splitlines()

        if len(linhas) < 60:
            return conteudo, False

        if len(set(linhas)) / len(linhas) >= 0.3:
            return conteudo, False

        vistos = set()

        for indice, linha in enumerate(linhas):
            if linha.startswith("#"):
                if linha in vistos:
                    return "\n".join(linhas[:indice]).rstrip(), True
                vistos.add(linha)

        return conteudo, False

    # =========================================================
    # PLANO (SEM API)
    # =========================================================

    def planejar_arquivo(self, pasta, nome, config):
        """
        Mostra, SEM chamar a API, o que acontecerá em cada página:
        assunto, método (textual/multimodal) e motivo.
        """
        caminho = Path(pasta) / nome

        if not caminho.exists():
            raise FileNotFoundError(f"PDF não encontrado: {caminho}")

        documento = pymupdf.open(caminho)
        linhas = []

        try:
            mapa = self.validar_arquivo(
                nome, config, len(documento)
            )
            textuais = set(config.get("paginas_textuais", []))
            multimodais = set(config.get("paginas_multimodais", []))

            for indice, pagina in enumerate(documento):
                numero = indice + 1
                assunto = mapa.get(numero)

                if assunto is None:
                    metodo, motivo = "ignorada", "fora_dos_assuntos"
                elif numero in multimodais:
                    metodo, motivo = "multimodal", "forcado_no_mapa"
                elif numero in textuais:
                    metodo, motivo = "textual", "forcado_no_mapa"
                else:
                    texto = (
                        self.document_processor
                        .extrair_texto_pagina(pagina)
                    )
                    analise = (
                        self.document_processor
                        .precisa_multimodal(pagina, texto)
                    )
                    if analise["precisa_multimodal"]:
                        metodo = "multimodal"
                        motivo = "deteccao_automatica"
                    else:
                        metodo, motivo = "textual", "deteccao_automatica"

                linhas.append({
                    "pagina": numero,
                    "assunto": assunto,
                    "metodo": metodo,
                    "motivo": motivo,
                })
        finally:
            documento.close()

        return linhas

    # =========================================================
    # PROCESSAR UM ARQUIVO
    # =========================================================

    def processar_arquivo(self, pasta, nome, config, periodo, disciplina):
        """
        Processa um PDF e devolve as páginas já rotuladas por assunto.
        """
        caminho = Path(pasta) / nome

        if not caminho.exists():
            raise FileNotFoundError(f"PDF não encontrado: {caminho}")

        documento = pymupdf.open(caminho)
        try:
            total = len(documento)
        finally:
            documento.close()

        mapa = self.validar_arquivo(nome, config, total)

        # Páginas fora dos assuntos viram "textuais forçadas":
        # assim nunca chamam a API (capa, página em branco...).
        ignoradas = {
            p for p in range(1, total + 1) if p not in mapa
        }

        textuais = set(config.get("paginas_textuais", [])) | ignoradas
        multimodais = set(config.get("paginas_multimodais", []))

        paginas = self.document_processor.processar_pdf(
            caminho_pdf=caminho,
            periodo=periodo,
            disciplina=disciplina,
            assunto=None,
            aula=config.get("aula"),
            paginas_multimodais=sorted(multimodais),
            paginas_textuais=sorted(textuais),
            usar_deteccao_automatica=True
        )

        resultado = []

        for pagina in paginas:
            metadata = pagina["metadata"]
            assunto = mapa.get(metadata["pagina"])

            if assunto is None:
                continue

            metadata["assunto"] = assunto

            if metadata["tipo_extracao"] == "multimodal":
                novo, corrigido = self.corrigir_repeticao(
                    pagina["conteudo"]
                )

                if corrigido:
                    print(
                        f"AVISO: repeticao detectada na pagina "
                        f"{metadata['pagina']}; texto cortado de "
                        f"{len(pagina['conteudo'])} para "
                        f"{len(novo)} caracteres."
                    )
                    pagina["conteudo"] = novo
                    metadata["motivos_deteccao"].append(
                        "multimodal_repeticao_truncada"
                    )

            if metadata["tipo_extracao"] == "textual":
                limpo = remover_repeticoes_consecutivas(
                    pagina["conteudo"]
                )

                if limpo != pagina["conteudo"]:
                    pagina["conteudo"] = limpo
                    metadata["motivos_deteccao"].append(
                        "texto_duplicado_removido"
                    )

            resultado.append(pagina)

        resultado, absorvidas = mesclar_paginas_curtas(resultado)

        if absorvidas:
            print(
                f"INFO: {absorvidas} paginas curtas mescladas "
                f"em {nome}."
            )

        return resultado, total

    # =========================================================
    # PROCESSAR A DISCIPLINA
    # =========================================================

    def processar_disciplina(self, pasta, mapa, arquivos=None):
        """
        Processa os arquivos do mapa (ou só os de 'arquivos').
        Retorna resumo por assunto, páginas e chunks.
        """
        periodo = mapa["periodo"]
        disciplina = mapa["disciplina"]

        todas_paginas = []
        todos_chunks = []
        resumo_arquivos = []

        for nome, config in mapa["arquivos"].items():

            if arquivos and nome not in arquivos:
                continue

            paginas, total = self.processar_arquivo(
                pasta, nome, config, periodo, disciplina
            )

            chunks = self.chunk_processor.processar_resultados(paginas)

            todas_paginas.extend(paginas)
            todos_chunks.extend(chunks)

            resumo_arquivos.append({
                "arquivo": nome,
                "total_paginas_pdf": total,
                "paginas_indexadas": len(paginas),
                "total_chunks": len(chunks),
            })

        por_assunto = {}

        for pagina in todas_paginas:
            m = pagina["metadata"]
            item = por_assunto.setdefault(
                m["assunto"],
                {"paginas": 0, "multimodais": 0, "chunks": 0}
            )
            item["paginas"] += 1
            if m["tipo_extracao"] == "multimodal":
                item["multimodais"] += 1

        for chunk in todos_chunks:
            por_assunto[chunk["metadata"]["assunto"]]["chunks"] += 1

        return {
            "periodo": periodo,
            "disciplina": disciplina,
            "arquivos": resumo_arquivos,
            "por_assunto": por_assunto,
            "total_chunks": len(todos_chunks),
            "paginas": todas_paginas,
            "chunks": todos_chunks,
        }

    # =========================================================
    # SALVAR JSON
    # =========================================================

    def salvar_json(self, dados, caminho_saida):
        caminho = Path(caminho_saida)
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
