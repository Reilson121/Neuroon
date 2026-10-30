"""Recuperação de questões no índice existente com permissões relacionais."""

import json


class QuestionRepository:
    def __init__(self, store=None):
        if store is None:
            from app.rag.vector_store import VectorStore
            store = VectorStore()
        self.store = store

    def buscar_questoes(self, disciplina_id, assunto_id, material_ids, origem, usar_teoria=False):
        if not material_ids:
            return []
        if usar_teoria:
            teoria = self.buscar_teoria(disciplina_id, assunto_id, material_ids, origem)
            if teoria:
                return teoria
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
            if linha['disciplina_slug']=='calculo_para_computacao_1':
                continue  # UP1 aberta: preservada no PDF e no Monitor, não vira uma objetiva original.
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

    def buscar_teoria(self, disciplina_id, assunto_id, material_ids, origem='MISTO'):
        """Somente a disciplina habilitada usa teoria; não simula lista ou prova."""
        from psycopg.rows import dict_row
        sql = """SELECT c.conteudo,c.metadata,c.pagina,c.arquivo,c.assunto,
                        m.id AS material_id,m.titulo,a.id AS assunto_id,d.slug AS disciplina_slug
                 FROM chunk_documento c
                 JOIN material m ON m.id=c.material_id
                 JOIN disciplina d ON d.id=m.disciplina_id
                 JOIN periodo p ON p.id=d.periodo_id
                 JOIN assunto a ON a.id=c.assunto_id AND a.disciplina_id=d.id
                 WHERE d.id=%s AND d.slug IN ('sistemas_digitais','estrutura_de_dados','calculo_para_computacao_1','calculo_para_computacao_2','estrutura_de_dados_avancada','design_de_artefatos_digitais') AND c.disciplina=d.slug
                   AND (d.slug='sistemas_digitais' OR
                     (d.slug IN ('estrutura_de_dados','calculo_para_computacao_1') AND p.numero=2) OR
                     (d.slug IN ('estrutura_de_dados_avancada','design_de_artefatos_digitais','calculo_para_computacao_2') AND p.numero=3))
                   AND m.id=ANY(%s) AND c.tipo_material=m.tipo
                   AND ((d.slug NOT IN ('calculo_para_computacao_1','calculo_para_computacao_2') AND m.tipo='SLIDE_AULA' AND (m.assunto_id=a.id OR (m.assunto_id IS NULL AND d.slug='estrutura_de_dados_avancada')) AND %s='MISTO')
                     OR (d.slug IN ('calculo_para_computacao_1','calculo_para_computacao_2') AND
                       ((m.tipo IN ('TRECHO_LIVRO','RESUMO') AND %s='MISTO') OR
                        (m.tipo='PROVA_ANTIGA' AND %s IN ('MISTO','PROVA') AND m.disponivel_para_pratica AND m.autorizacao_professor))))
                   AND c.assunto=a.slug
                   AND d.ativo AND d.possui_prova AND p.ativo AND a.ativo
                   AND m.ativo AND m.fonte_monitor_virtual
                   AND (%s::bigint IS NULL OR a.id=%s)
                 ORDER BY c.arquivo,c.pagina,c.chunk_index"""
        with self.store._conectar() as c:
            c.execute('SET TRANSACTION READ ONLY')
            c.execute("SET LOCAL statement_timeout='10s'")
            with c.cursor(row_factory=dict_row) as cur:
                cur.execute(sql,[disciplina_id,list(material_ids),origem,origem,origem,assunto_id,assunto_id])
                linhas=cur.fetchall()
        # Reúne chunks da mesma página para não separar a definição da sua explicação.
        paginas={}
        for r in linhas:
            # A prova de Cálculo reúne vários assuntos na mesma página.
            # Mesclar entre assuntos apagava a referência de fatoração/inversas.
            chave=(r['material_id'],r['pagina'],r['assunto_id'])
            if chave not in paginas:
                paginas[chave]=dict(disciplina_slug=r['disciplina_slug'], referencia_teorica=True,
                    assunto_id=r['assunto_id'], assunto_principal_proposto=r['assunto'],
                    conteudo='',fontes=[dict(material_id=r['material_id'],titulo_material=r['titulo'],
                        arquivo=r['arquivo'],pagina=r['pagina'],numero_questao=None)])
            paginas[chave]['conteudo']+='\n'+r['conteudo']
        return list(paginas.values())
