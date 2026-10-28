"""Sincronização transacional do índice derivado dos materiais processados."""

from app.rag.index_audit import comparar_chunks, ler_chunks


COLUNAS = (
    "periodo", "disciplina", "assunto", "aula", "arquivo",
    "tipo_arquivo", "tipo_extracao", "pagina", "chunk_index",
)


def planejar_sincronizacao(esperados, atuais, disciplina, permitir_insercao=False):
    if not esperados:
        raise ValueError("O JSON não pode estar vazio.")
    for chunk in esperados:
        metadata = chunk["metadata"]
        if metadata.get("disciplina") != disciplina:
            raise ValueError("O JSON contém outra disciplina.")
        if not chunk["conteudo"].strip() or any(
            metadata.get(campo) in (None, "")
            for campo in ("periodo", "arquivo", "tipo_extracao")
        ):
            raise ValueError("O JSON contém conteúdo vazio ou metadados incompletos.")
        if metadata.get("pagina") is None and not (
            metadata.get("tipo_arquivo") == "docx" and metadata.get("numero_questao")
        ):
            raise ValueError("Página ausente sem referência válida à questão de um DOCX.")
    arquivos = {c["metadata"]["arquivo"] for c in esperados}
    if any(
        c["metadata"].get("disciplina") != disciplina
        or c["metadata"].get("arquivo") not in arquivos
        for c in atuais
    ):
        raise ValueError("Há arquivos fora do conjunto processado; sincronização interrompida.")
    relatorio = comparar_chunks(esperados, atuais)
    # Este reparo é específico para o caso confirmado: IDs novos exigem revisão.
    if relatorio["faltantes"] and not permitir_insercao:
        raise ValueError("Há chunks ausentes; o índice mudou desde a verificação.")
    plano = {
        "remover": relatorio["extras"],
        "atualizar": sorted(set(relatorio["conteudos_divergentes"])
                            | set(relatorio["metadados_divergentes"])),
        "recalcular": relatorio["conteudos_divergentes"],
    }
    if permitir_insercao:
        plano["inserir"] = relatorio["faltantes"]
        plano["recalcular"] = sorted(set(plano["recalcular"]) | set(plano["inserir"]))
    return plano


def sincronizar_indice(store, esperados, disciplina, embedder=None, permitir_insercao=False, tipos_material=None, arquivos=None):
    from psycopg.types.json import Jsonb

    if tipos_material and any(c["metadata"].get("tipo_material") not in tipos_material for c in esperados):
        raise ValueError("O corpus contém materiais fora do escopo de sincronização.")
    if arquivos and any(c["metadata"].get("arquivo") not in arquivos for c in esperados):
        raise ValueError("O corpus contém arquivos fora do escopo de sincronização.")
    def ler(conexao):
        return ler_chunks(conexao, disciplina, tipos_material, arquivos) if arquivos else ler_chunks(conexao, disciplina, tipos_material)
    with store._conectar() as conexao:
        conexao.execute("SET TRANSACTION READ ONLY")
        conexao.execute("SET LOCAL statement_timeout = '10s'")
        antes = ler(conexao)
    plano = planejar_sincronizacao(esperados, antes, disciplina, permitir_insercao)
    resumo = {
        "chunks_antes": len(antes), "chunks_depois": len(esperados),
        "removidos": len(plano["remover"]),
        "atualizados": len(plano["atualizar"]),
        "embeddings_recalculados": len(plano["recalcular"]),
    }
    inserir = plano.get("inserir", [])
    if permitir_insercao:
        resumo["inseridos"] = len(inserir)
    if not plano["remover"] and not plano["atualizar"] and not inserir:
        return resumo

    origem = {c["chunk_id"]: c for c in esperados}
    destino = {c["chunk_id"]: c for c in antes}
    vetores = {}
    # A parte demorada acontece antes de abrir a transação de escrita.
    if plano["recalcular"]:
        if embedder is None:
            from app.rag.embedding_processor import EmbeddingProcessor
            embedder = EmbeddingProcessor()
        if embedder.dimensions != store.dimensao:
            raise ValueError("A dimensão do modelo difere da dimensão do índice.")
        for identificador in plano["recalcular"]:
            vetores[identificador] = store._vetor_para_texto(
                embedder.gerar_embedding(origem[identificador]["conteudo"])
            )

    linhas = []
    for identificador in plano["atualizar"]:
        chunk = origem[identificador]
        # Preserva campos extras existentes; os campos processados vêm do JSON.
        metadata = dict(destino[identificador]["metadata"])
        metadata.update(chunk["metadata"])
        colunas = [metadata.pop(c, None) for c in COLUNAS]
        metadata.pop("chunk_id", None)
        linhas.append((
            chunk["conteudo"], vetores.get(identificador), *colunas,
            Jsonb(metadata), disciplina, identificador,
        ))

    with store._conectar() as conexao:
        conexao.execute("SET LOCAL lock_timeout = '5s'")
        conexao.execute("SET LOCAL statement_timeout = '15s'")
        # Bloqueia escritas somente durante a breve aplicação, permitindo leituras.
        conexao.execute("LOCK TABLE chunk_documento IN SHARE ROW EXCLUSIVE MODE")
        if ler(conexao) != antes:
            raise RuntimeError("O índice mudou durante o cálculo. Nenhuma alteração foi aplicada.")
        for identificador in inserir:
            chunk = origem[identificador]
            metadata = dict(chunk["metadata"])
            colunas = [metadata.pop(c, None) for c in COLUNAS]
            metadata.pop("chunk_id", None)
            # Sem ON CONFLICT: um ID existente fora do escopo deve abortar,
            # nunca sobrescrever dados de outra disciplina.
            conexao.execute("""
                INSERT INTO chunk_documento (
                    chunk_id, conteudo, embedding, periodo, disciplina,
                    assunto, aula, arquivo, tipo_arquivo, tipo_extracao,
                    pagina, chunk_index, metadata
                ) VALUES (%s, %s, %s::vector, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s)
            """, (identificador, chunk["conteudo"], vetores[identificador],
                  *colunas, Jsonb(metadata)))
        for linha in linhas:
            resultado = conexao.execute("""
                UPDATE chunk_documento SET
                    conteudo = %s, embedding = COALESCE(%s::vector, embedding),
                    periodo = %s, disciplina = %s, assunto = %s, aula = %s,
                    arquivo = %s, tipo_arquivo = %s, tipo_extracao = %s,
                    pagina = %s, chunk_index = %s, metadata = %s
                WHERE disciplina = %s AND chunk_id = %s
            """, linha)
            if resultado.rowcount != 1:
                raise RuntimeError("A atualização não encontrou exatamente um chunk.")
        if plano["remover"]:
            resultado = conexao.execute("""
                DELETE FROM chunk_documento
                WHERE disciplina = %s AND chunk_id = ANY(%s)
            """, [disciplina, plano["remover"]])
            if resultado.rowcount != len(plano["remover"]):
                raise RuntimeError("A quantidade removida difere do plano.")
        if not comparar_chunks(esperados, ler(conexao))["compativel"]:
            raise RuntimeError("A conferência final falhou. A transação será desfeita.")
    return resumo
