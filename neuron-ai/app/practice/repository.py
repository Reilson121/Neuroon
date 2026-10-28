"""Recuperação de questões no índice existente com permissões relacionais."""

import json


class QuestionRepository:
    def __init__(self, store=None):
        if store is None:
            from app.rag.vector_store import VectorStore
            store = VectorStore()
        self.store = store

    def buscar_questoes(self, disciplina_id, assunto_id, material_ids, origem):
        if not material_ids:
            return []
        from psycopg.rows import dict_row
        from psycopg.types.json import Jsonb
        tipos = {"LISTA": ["LISTA_EXERCICIOS"], "PROVA": ["PROVA_ANTIGA"], "MISTO": ["LISTA_EXERCICIOS", "PROVA_ANTIGA"]}[origem]
        sql = """
            SELECT c.conteudo, c.metadata, m.id AS material_id,
                   m.titulo, m.tipo, d.slug AS disciplina_slug,
                   c.pagina, c.arquivo
            FROM chunk_documento c
            JOIN material m ON m.id = COALESCE(c.material_id, (c.metadata->>'material_id')::bigint)
            JOIN disciplina d ON d.id = m.disciplina_id
            JOIN periodo p ON p.id = d.periodo_id
            WHERE m.disciplina_id = %s AND m.id = ANY(%s)
              AND c.disciplina = d.slug
              AND m.tipo = ANY(%s)
              AND COALESCE(c.tipo_material,c.metadata->>'tipo_material') = m.tipo
              AND m.ativo AND m.disponivel_para_pratica AND m.autorizacao_professor
              AND d.ativo AND d.possui_prova AND p.ativo
              AND EXISTS (SELECT 1 FROM assunto a
                          WHERE a.id=COALESCE(c.assunto_id,(c.metadata->>'assunto_id')::bigint)
                            AND a.disciplina_id=d.id AND a.ativo)
        """
        params = [disciplina_id, list(material_ids), tipos]
        if assunto_id is not None:
            sql += """ AND (COALESCE(c.assunto_id,(c.metadata->>'assunto_id')::bigint) = %s
                        OR c.metadata->'assunto_ids' @> %s)
                       AND EXISTS (SELECT 1 FROM assunto a WHERE a.id=%s AND a.disciplina_id=d.id AND a.ativo)
            """
            params.extend([assunto_id, Jsonb([assunto_id]), assunto_id])
        sql += " ORDER BY c.chunk_id LIMIT 200"
        with self.store._conectar() as conexao:
            conexao.execute("SET TRANSACTION READ ONLY")
            conexao.execute("SET LOCAL statement_timeout = '10s'")
            with conexao.cursor(row_factory=dict_row) as cursor:
                cursor.execute(sql, params)
                linhas = cursor.fetchall()
        grupos = {}
        for linha in linhas:
            questao = json.loads(linha["conteudo"])
            ref = questao["referencia_local"]
            fonte = {"material_id": linha["material_id"], "titulo_material": linha["titulo"],
                     "arquivo": linha["arquivo"], "pagina": linha["pagina"],
                     "numero_questao": str(linha["metadata"]["numero_questao"])}
            if ref not in grupos:
                grupos[ref] = {**questao, "fontes": [], "disciplina_slug": linha["disciplina_slug"],
                               "assunto_id": linha["metadata"]["assunto_id"],
                               "assunto_ids": linha["metadata"].get("assunto_ids", []),
                               "assuntos_por_id": linha["metadata"].get("assuntos_por_id", {})}
            grupos[ref]["fontes"].append(fonte)
        for questao in grupos.values():
            # Um gabarito de outra origem não atravessa sua autorização revogada.
            gabarito = questao.get("gabarito_material")
            if gabarito and gabarito.get("arquivo") not in {f["arquivo"] for f in questao["fontes"]}:
                questao["gabarito_material"] = None
        return list(grupos.values())
