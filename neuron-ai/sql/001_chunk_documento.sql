-- NEURON - tabela de chunks para busca vetorial (prototipo do servico de IA)
-- Requer a extensao pgvector. Dimensao 384 = paraphrase-multilingual-MiniLM-L12-v2.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunk_documento (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chunk_id VARCHAR(64) NOT NULL UNIQUE,
    conteudo TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,

    -- metadados atuais do RAG
    periodo VARCHAR(10) NOT NULL,
    disciplina VARCHAR(150) NOT NULL,
    assunto VARCHAR(150),
    aula VARCHAR(20),
    arquivo VARCHAR(255) NOT NULL,
    tipo_arquivo VARCHAR(20),
    tipo_extracao VARCHAR(20) NOT NULL,
    pagina INTEGER,
    chunk_index INTEGER,

    -- previstos na modelagem; preenchidos quando o banco relacional existir
    material_id BIGINT,
    periodo_id BIGINT,
    disciplina_id BIGINT,
    assunto_id BIGINT,
    tipo_material VARCHAR(40),
    titulo_material VARCHAR(200),

    -- demais campos do chunk (motivos_deteccao etc.)
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_chunk_tipo_extracao
        CHECK (tipo_extracao IN ('textual', 'multimodal'))
);

CREATE INDEX IF NOT EXISTS ix_chunk_disciplina_assunto
    ON chunk_documento (disciplina, assunto);

CREATE INDEX IF NOT EXISTS ix_chunk_embedding_hnsw
    ON chunk_documento USING hnsw (embedding vector_cosine_ops);
