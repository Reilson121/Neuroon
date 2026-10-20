import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkProcessor:
    """
    Responsável por dividir o conteúdo acadêmico
    processado em pequenos trechos para o RAG.

    Cada chunk preserva os metadados da página original.
    """

    def __init__(
        self,
        chunk_size=1000,
        chunk_overlap=150
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap deve ser menor que chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,

            # A ordem importa.
            # Primeiro tentamos quebrar em blocos maiores
            # e semanticamente mais naturais.
            separators=[
                "\n\n",
                "\n",
                ". ",
                "; ",
                ", ",
                " ",
                ""
            ]
        )

    # =========================================================
    # ID DETERMINÍSTICO
    # =========================================================

    def gerar_chunk_id(
        self,
        metadata,
        indice_chunk
    ):
        """
        Gera um identificador estável para o chunk.

        Isso será útil posteriormente para:
        - PostgreSQL;
        - pgvector;
        - reindexação;
        - evitar duplicações.
        """

        periodo = metadata.get(
            "periodo",
            ""
        )

        disciplina = metadata.get(
            "disciplina",
            ""
        )

        aula = metadata.get(
            "aula",
            ""
        )

        arquivo = metadata.get(
            "arquivo",
            ""
        )

        pagina = metadata.get(
            "pagina",
            ""
        )

        base_id = (
            f"{periodo}|"
            f"{disciplina}|"
            f"{aula}|"
            f"{arquivo}|"
            f"{pagina}|"
            f"{indice_chunk}"
        )

        return hashlib.sha256(
            base_id.encode("utf-8")
        ).hexdigest()[:24]

    # =========================================================
    # NORMALIZAÇÃO DOS METADADOS
    # =========================================================

    def extrair_metadata(self, item):
        """
        Aceita os dois formatos que temos atualmente:

        1. Saída padrão do DocumentProcessor:
           {
               "conteudo": "...",
               "metadata": {...}
           }

        2. JSON do nosso teste:
           {
               "arquivo": "...",
               "pagina": 1,
               ...
               "conteudo": "..."
           }
        """

        if "metadata" in item:

            return dict(
                item["metadata"]
            )

        # Para os resultados antigos do teste,
        # tudo menos "conteudo" vira metadata.
        return {
            chave: valor
            for chave, valor in item.items()
            if chave != "conteudo"
        }

    # =========================================================
    # DIVISÃO DE UM ITEM
    # =========================================================

    def processar_item(self, item):
        """
        Divide uma página/documento processado
        em chunks.
        """

        conteudo = (
            item
            .get("conteudo", "")
            .strip()
        )

        if not conteudo:
            return []

        metadata_original = (
            self.extrair_metadata(
                item
            )
        )

        textos = (
            self.splitter.split_text(
                conteudo
            )
        )

        total_chunks = len(
            textos
        )

        chunks = []

        for indice, texto_chunk in enumerate(
            textos,
            start=1
        ):

            metadata = dict(
                metadata_original
            )

            metadata[
                "chunk_index"
            ] = indice

            metadata[
                "total_chunks_pagina"
            ] = total_chunks

            metadata[
                "chunk_caracteres"
            ] = len(
                texto_chunk
            )

            chunk_id = (
                self.gerar_chunk_id(
                    metadata,
                    indice
                )
            )

            metadata[
                "chunk_id"
            ] = chunk_id

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "conteudo": texto_chunk.strip(),
                    "metadata": metadata
                }
            )

        return chunks

    # =========================================================
    # PROCESSAMENTO DE VÁRIOS RESULTADOS
    # =========================================================

    def processar_resultados(
        self,
        resultados
    ):
        """
        Recebe uma lista de páginas/documentos
        processados e retorna todos os chunks.
        """

        todos_chunks = []

        for item in resultados:

            chunks_item = (
                self.processar_item(
                    item
                )
            )

            todos_chunks.extend(
                chunks_item
            )

        return todos_chunks