"""Comparação somente para leitura entre o índice e os chunks processados."""


def comparar_chunks(esperados, atuais):
    def indexar(chunks):
        indice = {c["chunk_id"]: c for c in chunks}
        if len(indice) != len(chunks):
            raise ValueError("A base contém chunk_id duplicado.")
        return indice

    esperado = indexar(esperados)
    atual = indexar(atuais)
    comuns = esperado.keys() & atual.keys()
    conteudos_divergentes = []
    metadados_divergentes = []
    for identificador in sorted(comuns):
        origem = esperado[identificador]
        destino = atual[identificador]
        if origem["conteudo"] != destino["conteudo"]:
            conteudos_divergentes.append(identificador)
        if any(
            destino["metadata"].get(chave) != valor
            for chave, valor in origem["metadata"].items()
        ):
            metadados_divergentes.append(identificador)
    faltantes = sorted(esperado.keys() - atual.keys())
    extras = sorted(atual.keys() - esperado.keys())
    return {
        "compativel": not any((faltantes, extras, conteudos_divergentes, metadados_divergentes)),
        "chunks_json": len(esperado), "chunks_banco": len(atual),
        "faltantes": faltantes, "extras": extras,
        "conteudos_divergentes": conteudos_divergentes,
        "metadados_divergentes": metadados_divergentes,
    }


def ler_chunks(conexao, disciplina, tipos_material=None, arquivos=None):
    """Lê os chunks com metadados normalizados usando a transação do chamador."""
    from psycopg.rows import dict_row

    with conexao.cursor(row_factory=dict_row) as cursor:
        sql = """
            SELECT chunk_id, conteudo, periodo, disciplina, assunto, aula,
                   arquivo, tipo_arquivo, tipo_extracao, pagina, chunk_index,
                   metadata
            FROM chunk_documento WHERE disciplina = %s
        """
        params = [disciplina]
        if tipos_material:
            # Chunks legados das aulas foram indexados antes do catálogo e
            # ainda não têm tipo. O Monitor já os interpreta como SLIDE_AULA.
            sql += " AND COALESCE(tipo_material,metadata->>'tipo_material','SLIDE_AULA') = ANY(%s)"
            params.append(list(tipos_material))
        if arquivos:
            sql += " AND arquivo = ANY(%s)"
            params.append(list(arquivos))
        sql += " ORDER BY chunk_id"
        cursor.execute(sql, params)
        atuais = []
        for linha in cursor.fetchall():
            metadata = dict(linha["metadata"] or {})
            metadata.update({
                chave: valor for chave, valor in linha.items()
                if chave not in {"metadata", "conteudo"}
            })
            atuais.append({
                "chunk_id": linha["chunk_id"], "conteudo": linha["conteudo"],
                "metadata": metadata,
            })
    return atuais


def auditar_indice(store, esperados, disciplina, tipos_material=None):
    if not esperados or any(
        c["metadata"].get("disciplina") != disciplina for c in esperados
    ):
        raise ValueError("O JSON deve conter chunks somente da disciplina informada.")
    # Usa uma única fotografia do banco e não escreve no índice.
    from psycopg.rows import dict_row

    with store._conectar() as conexao:
        conexao.execute("SET TRANSACTION READ ONLY")
        conexao.execute("SET LOCAL statement_timeout = '10s'")
        with conexao.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            extensao = cursor.fetchone()
            cursor.execute("""
                SELECT format_type(atttypid, atttypmod) AS tipo
                FROM pg_attribute
                WHERE attrelid = 'chunk_documento'::regclass
                AND attname = 'embedding' AND NOT attisdropped
            """)
            coluna = cursor.fetchone()
        atuais = ler_chunks(conexao, disciplina, tipos_material)
    relatorio = comparar_chunks(esperados, atuais)
    relatorio["pgvector"] = extensao["extversion"] if extensao else None
    relatorio["tipo_embedding"] = coluna["tipo"] if coluna else None
    relatorio["compativel"] = (
        relatorio["compativel"] and relatorio["pgvector"] is not None
        and relatorio["tipo_embedding"] == "vector(384)"
    )
    return relatorio
