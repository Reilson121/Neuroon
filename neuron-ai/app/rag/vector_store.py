import math
import os

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()


# Campos do metadata que viram colunas da tabela chunk_documento.
# Todo o resto do metadata vai para a coluna JSONB "metadata".
COLUNAS_METADATA = [
    "periodo",
    "disciplina",
    "assunto",
    "aula",
    "arquivo",
    "tipo_arquivo",
    "tipo_extracao",
    "pagina",
    "chunk_index",
]

OBRIGATORIOS = ["periodo", "disciplina", "arquivo", "tipo_extracao"]


class VectorStore:
    """
    Persistência dos chunks e embeddings no PostgreSQL + pgvector.

    A conexão usa variáveis do arquivo .env:
        DB_HOST (padrão localhost), DB_PORT (5432), DB_NAME (neuron),
        DB_USER (postgres) e DB_PASSWORD (obrigatória).

    O banco relacional é a fonte de verdade; esta tabela é um índice
    derivado e pode ser reconstruída a partir dos materiais.
    """

    def __init__(self, dimensao=384):
        senha = os.getenv("DB_PASSWORD")

        if not senha:
            raise RuntimeError(
                "DB_PASSWORD não definida. Adicione ao arquivo .env."
            )

        self.dimensao = dimensao
        self.conexao = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "dbname": os.getenv("DB_NAME", "neuron"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": senha,
        }

    def _conectar(self):
        return psycopg.connect(**self.conexao)

    # =========================================================
    # CONVERSÃO DO VETOR
    # =========================================================

    def _vetor_para_texto(self, embedding):
        """
        Converte a lista de floats para o formato '[0.1,0.2,...]'
        aceito pelo tipo vector do pgvector.
        """
        if len(embedding) != self.dimensao:
            raise ValueError(
                f"Embedding com {len(embedding)} dimensões; "
                f"esperado {self.dimensao}."
            )

        if not all(math.isfinite(x) for x in embedding):
            raise ValueError("Embedding contém NaN ou infinito.")

        return "[" + ",".join(repr(float(x)) for x in embedding) + "]"

    # =========================================================
    # SALVAR (UPSERT)
    # =========================================================

    def salvar_chunks(self, chunks_com_embedding):
        """
        Salva chunks que já possuem 'embedding'.
        Se o chunk_id já existir, atualiza (não duplica).
        Tudo ocorre em uma única transação.
        """
        linhas = []

        for chunk in chunks_com_embedding:
            metadata = dict(chunk["metadata"])

            faltando = [
                c for c in OBRIGATORIOS if metadata.get(c) in (None, "")
            ]
            if faltando:
                raise ValueError(
                    f"Chunk {chunk['chunk_id']} sem campos "
                    f"obrigatórios: {faltando}"
                )

            colunas = [metadata.pop(c, None) for c in COLUNAS_METADATA]
            metadata.pop("chunk_id", None)

            linhas.append((
                chunk["chunk_id"],
                chunk["conteudo"],
                self._vetor_para_texto(chunk["embedding"]),
                *colunas,
                Jsonb(metadata),
            ))

        sql = """
            INSERT INTO chunk_documento (
                chunk_id, conteudo, embedding,
                periodo, disciplina, assunto, aula, arquivo,
                tipo_arquivo, tipo_extracao, pagina, chunk_index,
                metadata
            )
            VALUES (%s, %s, %s::vector,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET
                conteudo = EXCLUDED.conteudo,
                embedding = EXCLUDED.embedding,
                periodo = EXCLUDED.periodo,
                disciplina = EXCLUDED.disciplina,
                assunto = EXCLUDED.assunto,
                aula = EXCLUDED.aula,
                arquivo = EXCLUDED.arquivo,
                tipo_arquivo = EXCLUDED.tipo_arquivo,
                tipo_extracao = EXCLUDED.tipo_extracao,
                pagina = EXCLUDED.pagina,
                chunk_index = EXCLUDED.chunk_index,
                metadata = EXCLUDED.metadata
        """

        with self._conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.executemany(sql, linhas)

        return len(linhas)

    # =========================================================
    # CONSULTAS SIMPLES
    # =========================================================

    def contar(self, disciplina=None):
        sql = "SELECT count(*) FROM chunk_documento"
        params = []

        if disciplina:
            sql += " WHERE disciplina = %s"
            params.append(disciplina)

        with self._conectar() as conexao:
            return conexao.execute(sql, params).fetchone()[0]

    def resumo_por_assunto(self, disciplina):
        sql = """
            SELECT assunto, count(*) AS chunks,
                   count(DISTINCT arquivo) AS arquivos
            FROM chunk_documento
            WHERE disciplina = %s
            GROUP BY assunto
            ORDER BY min(id)
        """

        with self._conectar() as conexao:
            return conexao.execute(sql, [disciplina]).fetchall()

    # =========================================================
    # REMOVER (reindexação)
    # =========================================================

    def remover_por_arquivo(self, disciplina, arquivo):
        """
        Remove os chunks de um arquivo (usado antes de reindexar).
        Retorna quantos foram removidos.
        """
        sql = """
            DELETE FROM chunk_documento
            WHERE disciplina = %s AND arquivo = %s
        """

        with self._conectar() as conexao:
            return conexao.execute(sql, [disciplina, arquivo]).rowcount


    # =========================================================
    # BUSCA VETORIAL (TOP-K)
    # =========================================================

    @staticmethod
    def _filtro_monitor(conexao):
        filtro = """
            AND COALESCE(tipo_material,metadata->>'tipo_material','SLIDE_AULA')
                NOT IN ('LISTA_EXERCICIOS','PROVA_ANTIGA')
            AND COALESCE(metadata->>'fonte_monitor_virtual','true') = 'true'
        """
        # O protótipo anterior não possui o núcleo relacional. Depois da
        # migration, IDs vinculados sempre obedecem às permissões atuais.
        existe = conexao.execute("SELECT to_regclass('material')").fetchone()[0]
        if existe:
            filtro += """
                  AND ((COALESCE(material_id,(metadata->>'material_id')::bigint) IS NULL
                        AND NOT EXISTS (SELECT 1 FROM disciplina cadastrada WHERE cadastrada.slug=chunk_documento.disciplina)) OR EXISTS (
                    SELECT 1 FROM material m
                    JOIN disciplina d ON d.id=m.disciplina_id
                    JOIN periodo p ON p.id=d.periodo_id
                    WHERE m.id=COALESCE(chunk_documento.material_id,(chunk_documento.metadata->>'material_id')::bigint)
                      AND m.ativo AND m.fonte_monitor_virtual AND d.ativo AND p.ativo
                      AND d.slug=chunk_documento.disciplina
                      AND (COALESCE(chunk_documento.assunto_id,(chunk_documento.metadata->>'assunto_id')::bigint) IS NULL
                           OR EXISTS (SELECT 1 FROM assunto a WHERE a.id=COALESCE(chunk_documento.assunto_id,(chunk_documento.metadata->>'assunto_id')::bigint)
                                      AND a.disciplina_id=d.id AND a.ativo))
                ))
            """
        return filtro

    def buscar_similares(self, embedding, disciplina, assunto=None, k=5):
        """
        Retorna os k chunks mais parecidos com o embedding da pergunta,
        sempre restritos a uma disciplina (e, opcionalmente, a um
        assunto).

        Usa distancia de cosseno: similaridade = 1 - distancia
        (perto de 1.0 = muito parecido; perto de 0 = sem relacao).
        """
        from psycopg.rows import dict_row

        if not disciplina:
            raise ValueError("A disciplina e obrigatoria na busca.")

        if not 1 <= k <= 50:
            raise ValueError("k deve estar entre 1 e 50.")

        vetor = self._vetor_para_texto(embedding)

        sql = """
            SELECT chunk_id, conteudo, periodo, disciplina, assunto, aula,
                   arquivo, pagina, tipo_arquivo, tipo_extracao, chunk_index,
                   material_id, periodo_id, disciplina_id, assunto_id,
                   tipo_material, titulo_material, metadata,
                   1 - (embedding <=> %s::vector) AS similaridade
            FROM chunk_documento
            WHERE disciplina = %s
        """
        params = [vetor, disciplina]

        if assunto:
            sql += " AND assunto = %s"
            params.append(assunto)

        params.extend([vetor, k])

        with self._conectar() as conexao:
            sql += self._filtro_monitor(conexao)
            sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
            with conexao.cursor(row_factory=dict_row) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()

    def buscar_hibridos(self, embedding, pergunta, disciplina, assunto=None, k=5):
        """Busca exata e BM25 no conjunto pequeno de uma disciplina do MVP."""
        from psycopg.rows import dict_row
        from app.rag.hybrid_search import ordenar_hibrido

        if not disciplina or not 1 <= k <= 50:
            raise ValueError("Informe disciplina e k entre 1 e 50.")
        sql = """
            SELECT chunk_id, conteudo, periodo, disciplina, assunto, aula,
                   arquivo, pagina, tipo_arquivo, tipo_extracao, chunk_index,
                   material_id, periodo_id, disciplina_id, assunto_id,
                   tipo_material, titulo_material, metadata,
                   1 - (embedding <=> %s::vector) AS similaridade
            FROM chunk_documento WHERE disciplina = %s
        """
        params = [self._vetor_para_texto(embedding), disciplina]
        if assunto:
            sql += " AND assunto = %s"
            params.append(assunto)
        with self._conectar() as conexao:
            sql += self._filtro_monitor(conexao)
            with conexao.cursor(row_factory=dict_row) as cursor:
                cursor.execute(sql, params)
                linhas = cursor.fetchall()
        return ordenar_hibrido(linhas, pergunta, k)
