from sentence_transformers import SentenceTransformer


class EmbeddingProcessor:
    """
    Responsável pela geração de embeddings
    dos conteúdos utilizados pelo RAG.
    """

    def __init__(
        self,
        model_name=(
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )
    ):
        self.model_name = model_name

        print(
            f"Carregando modelo de embeddings: "
            f"{self.model_name}"
        )

        self.model = SentenceTransformer(
            self.model_name
        )

        self.dimensions = (
            self.model.get_sentence_embedding_dimension()
        )

    # =========================================================
    # EMBEDDING DE TEXTO
    # =========================================================

    def gerar_embedding(self, texto):
        """
        Gera embedding para um único texto.
        """

        if not texto:
            raise ValueError(
                "O texto para embedding está vazio."
            )

        embedding = self.model.encode(
            texto,
            normalize_embeddings=True
        )

        return embedding.tolist()

    # =========================================================
    # EMBEDDINGS DOS CHUNKS
    # =========================================================

    def processar_chunks(self, chunks):
        """
        Adiciona um embedding a cada chunk.
        """

        resultados = []

        for chunk in chunks:

            conteudo = (
                chunk
                .get("conteudo", "")
                .strip()
            )

            if not conteudo:
                continue

            embedding = (
                self.gerar_embedding(
                    conteudo
                )
            )

            resultados.append(
                {
                    "chunk_id": (
                        chunk["chunk_id"]
                    ),
                    "conteudo": conteudo,
                    "metadata": (
                        chunk["metadata"]
                    ),
                    "embedding": embedding
                }
            )

        return resultados