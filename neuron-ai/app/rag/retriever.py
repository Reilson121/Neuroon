"""Recuperação de contexto no pgvector, sem chamar o modelo de linguagem."""

import math


# A busca lexical complementa o embedding para definições curtas nos slides.
DISCIPLINAS_HIBRIDAS = {"design_de_artefatos_digitais", "projeto_de_ideacao_de_software",
                       "estrutura_de_dados_avancada"}


class Retriever:
    def __init__(self, embedder=None, store=None):
        # Importações tardias permitem testes sem modelo, banco ou credenciais.
        if store is None:
            from app.rag.vector_store import VectorStore
            store = VectorStore()
        if embedder is None:
            from app.rag.embedding_processor import EmbeddingProcessor
            embedder = EmbeddingProcessor()
        self.embedder = embedder
        self.store = store

    def recuperar(self, pergunta, disciplina, assunto=None, k=5):
        if not isinstance(pergunta, str) or not pergunta.strip():
            raise ValueError("Informe uma pergunta não vazia.")
        if not isinstance(disciplina, str) or not disciplina.strip():
            raise ValueError("A disciplina é obrigatória.")
        if assunto is not None and (
            not isinstance(assunto, str) or not assunto.strip()
        ):
            raise ValueError("O assunto deve ser preenchido ou omitido.")
        if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 50:
            raise ValueError("k deve ser um inteiro entre 1 e 50.")

        embedding = self.embedder.gerar_embedding(pergunta.strip())
        filtros = {"assunto": assunto.strip() if assunto is not None else None, "k": k}
        if disciplina.strip() in DISCIPLINAS_HIBRIDAS:
            consulta_lexical = pergunta.strip()
            if disciplina.strip() == 'estrutura_de_dados_avancada':
                from app.rag.ed_avancada_search import expandir_variantes
                consulta_lexical = expandir_variantes(consulta_lexical)
            if disciplina.strip() == "projeto_de_ideacao_de_software":
                from app.rag.ideacao_search import expandir_siglas, ordenar_evidencias
                consulta_lexical = expandir_siglas(consulta_lexical)
                candidatos = self.store.buscar_hibridos(
                    embedding, consulta_lexical, disciplina.strip(),
                    assunto=filtros["assunto"], k=50)
                linhas = ordenar_evidencias(candidatos, pergunta.strip(), k)
            else:
                linhas = self.store.buscar_hibridos(embedding, consulta_lexical, disciplina.strip(), **filtros)
        else:
            linhas = self.store.buscar_similares(embedding, disciplina.strip(), **filtros)
        resultados = []
        for linha in linhas:
            similaridade = float(linha["similaridade"])
            if not math.isfinite(similaridade):
                raise ValueError("A busca retornou similaridade inválida.")
            metadata = dict(linha.get("metadata") or {})
            metadata.update({
                chave: valor for chave, valor in linha.items()
                if chave not in {"metadata", "conteudo", "similaridade", "cobertura_lexical"}
                and (valor is not None or chave not in metadata)
            })
            resultados.append({
                "chunk_id": linha["chunk_id"],
                "conteudo": linha["conteudo"],
                "metadata": metadata,
                "similaridade": similaridade,
                **({"cobertura_lexical": linha["cobertura_lexical"]} if "cobertura_lexical" in linha else {}),
            })
        return resultados
