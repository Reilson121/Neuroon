"""Índice derivado dos materiais aprovados; banco relacional governa acesso.

Não aceita caminhos enviados pelo cliente. Usa os corpora locais conferidos
de Estatística, Estrutura de Dados Avançada e Design de Artefatos Digitais.
"""
import copy
import hashlib
import json
from pathlib import Path
from psycopg.rows import dict_row
from app.rag.vector_store import VectorStore
from app.rag.index_sync import sincronizar_indice

ROOT = Path(__file__).resolve().parents[2]
PROPOSTAS = ROOT / "propostas" / "estatistica"
MATERIAIS = ROOT / "materiais_academicos" / "periodo_03" / "estatistica"


def catalogo(store, disciplina='estatistica'):
    if disciplina not in {'estatistica', 'estrutura_de_dados_avancada', 'design_de_artefatos_digitais'}:
        raise ValueError('Disciplina sem corpus preparado.')
    with store._conectar() as c:
        c.execute("SET TRANSACTION READ ONLY")
        with c.cursor(row_factory=dict_row) as cur:
            cur.execute("""SELECT m.*,d.slug AS disciplina_slug,d.ativo AS disciplina_ativa,
                d.possui_prova,p.ativo AS periodo_ativo,p.numero AS periodo_numero,p.id AS periodo_id
                FROM material m JOIN disciplina d ON d.id=m.disciplina_id
                JOIN periodo p ON p.id=d.periodo_id WHERE d.slug=%s""", [disciplina])
            materiais = cur.fetchall()
            cur.execute("SELECT a.* FROM assunto a JOIN disciplina d ON d.id=a.disciplina_id WHERE d.slug=%s", [disciplina])
            assuntos = cur.fetchall()
    return materiais, {a["slug"]: a for a in assuntos}


def permitido(m):
    base = m["ativo"] and m["disciplina_ativa"] and m["periodo_ativo"]
    if m["tipo"] == "SLIDE_AULA":
        return base and m["fonte_monitor_virtual"]
    return base and m["tipo"] in {"LISTA_EXERCICIOS", "PROVA_ANTIGA"} and m["possui_prova"] and m["autorizacao_professor"] and m["disponivel_para_pratica"]


def origem_local(m, inventario):
    ref = m["referencia_externa"]
    registro = next((r for r in inventario["arquivos"] if ref == "local:materiais_academicos/periodo_03/estatistica/" + r["arquivo_original"]), None)
    if not registro or registro.get("fora_da_disciplina"):
        raise ValueError("Origem não preparada para indexação.")
    arquivo = MATERIAIS / registro["arquivo_original"]
    if arquivo.resolve().parent != MATERIAIS.resolve() or hashlib.sha256(arquivo.read_bytes()).hexdigest() != registro["sha256"]:
        raise ValueError("Arquivo original diverge do inventário aprovado.")
    return registro


def preparar(m, assuntos, inventario):
    r = origem_local(m, inventario)
    if not permitido(m):
        raise ValueError("Material não está autorizado/disponível no cadastro.")
    if m["tipo"] == "SLIDE_AULA":
        from app.rag.estatistica_corpus import carregar_validado
        chunks = copy.deepcopy(carregar_validado()["chunks"])
    else:
        refs = json.loads((PROPOSTAS / "avaliacoes_preparadas.json").read_text(encoding="utf-8"))
        chunks = []
        for q in refs["questoes"]:
            for fonte in q["origens"]:
                if fonte["arquivo"] != r["arquivo_original"]:
                    continue
                if fonte["sha256"] != r["sha256"] or fonte["tipo_material"] != m["tipo"]:
                    raise ValueError("Referência acadêmica inconsistente.")
                slug = q["assunto_principal_proposto"]
                slugs = [slug, *q.get("assuntos_secundarios_propostos", [])]
                if any(s not in assuntos or not assuntos[s]["ativo"] or assuntos[s]["disciplina_id"] != m["disciplina_id"] for s in slugs):
                    raise ValueError("Assunto da questão indisponível ou de outra disciplina.")
                # Questão completa, incluindo subitens: nunca recortada em texto.
                payload = copy.deepcopy(q)
                payload.pop("origens", None)
                identity = f"estatistica|{r['sha256']}|questao|{fonte['numero_questao']}"
                meta = {"periodo":"03","disciplina":"estatistica","aula":None,
                        "assunto":slug,"arquivo":r["arquivo_original"],"pagina":fonte["pagina"],
                        "tipo_arquivo":Path(r["arquivo_original"]).suffix[1:],
                        "tipo_extracao":"textual" if Path(r["arquivo_original"]).suffix.lower()=='.docx' else "multimodal",
                        "transcricao_conferida":True,"metodo_preparo":"transcricao_conferida_manualmente",
                        "tipo_material":m["tipo"],"numero_questao":fonte["numero_questao"],"chunk_index":0,
                        "documento_sha256":r["sha256"],"assunto_ids":[assuntos[s]["id"] for s in slugs],
                        "assuntos_por_id":{str(assuntos[s]["id"]):s for s in slugs},
                        "gabarito_oficial_professor":None,
                        "metadados_documento_originais":r.get("metadados_pdf_originais",r.get("metadados_docx_originais"))}
                chunks.append({"chunk_id":hashlib.sha256(identity.encode()).hexdigest()[:24],
                               "conteudo":json.dumps(payload,ensure_ascii=False,sort_keys=True),"metadata":meta})
    for chunk in chunks:
        meta = chunk["metadata"]
        a = assuntos[meta["assunto"]]
        if not a["ativo"] or a["disciplina_id"] != m["disciplina_id"]:
            raise ValueError("Assunto indisponível ou de outra disciplina.")
        meta.setdefault("titulo_material",m["titulo"])
        meta.update(material_id=m["id"],periodo_id=m["periodo_id"],disciplina_id=m["disciplina_id"],assunto_id=a["id"],
                    titulo_cadastro_material=m["titulo"],fonte_monitor_virtual=m["fonte_monitor_virtual"],
                    autorizacao_professor=m["autorizacao_professor"],disponivel_para_pratica=m["disponivel_para_pratica"])
    return chunks


def indexar(material_id, store=None):
    store = store or VectorStore()
    with store._conectar() as c:
        linha = c.execute('SELECT d.slug FROM material m JOIN disciplina d ON d.id=m.disciplina_id WHERE m.id=%s', [material_id]).fetchone()
    if not linha:
        raise ValueError('Material não encontrado.')
    disciplina = linha[0]
    materiais, assuntos = catalogo(store, disciplina)
    m = next((m for m in materiais if m["id"] == material_id), None)
    if m is None:
        raise ValueError("Material não preparado nesta integração.")
    # Escopo por arquivo evita apagar outros materiais do mesmo tipo.
    if disciplina == 'estrutura_de_dados_avancada':
        from app.rag.ed_avancada_corpus import preparar_material
        chunks = preparar_material(m, assuntos)
    elif disciplina == 'design_de_artefatos_digitais':
        from app.rag.design_corpus import preparar_material
        chunks = preparar_material(m, assuntos)
    else:
        inventario = json.loads((PROPOSTAS / "inventario.json").read_text(encoding="utf-8"))
        chunks = preparar(m, assuntos, inventario)
    if not chunks:
        raise ValueError("Material sem conteúdo preparado e conferido.")
    # O sincronizador aceita o filtro de arquivos além do tipo; nenhuma implementação paralela.
    resultado = sincronizar_indice(store, chunks, disciplina, permitir_insercao=True,
                                  tipos_material=[m["tipo"]], arquivos=[chunks[0]["metadata"]["arquivo"]])
    # O protótipo já tinha colunas relacionais opcionais. Mantém também esses
    # campos preenchidos, além da proveniência integral no JSONB.
    with store._conectar() as c:
        c.execute("SET LOCAL statement_timeout='15s'")
        vinculados=c.execute("""UPDATE chunk_documento c SET material_id=m.id,
            periodo_id=%s,disciplina_id=m.disciplina_id,assunto_id=a.id,tipo_material=m.tipo,
            titulo_material=COALESCE(c.metadata->>'titulo_material',m.titulo)
            FROM material m JOIN assunto a ON a.disciplina_id=m.disciplina_id
            WHERE m.id=%s AND a.id=(c.metadata->>'assunto_id')::bigint
              AND c.disciplina=%s AND c.chunk_id=ANY(%s)
              AND (c.material_id,c.periodo_id,c.disciplina_id,c.assunto_id,c.tipo_material,c.titulo_material)
                  IS DISTINCT FROM (m.id,%s,m.disciplina_id,a.id,m.tipo,COALESCE(c.metadata->>'titulo_material',m.titulo))
        """,[m['periodo_id'],material_id,disciplina,[q['chunk_id'] for q in chunks],m['periodo_id']]).rowcount
        total=c.execute("""SELECT count(*) FROM chunk_documento
            WHERE material_id=%s AND disciplina_id=%s AND assunto_id IS NOT NULL
              AND chunk_id=ANY(%s)""",[material_id,m['disciplina_id'],[q['chunk_id'] for q in chunks]]).fetchone()[0]
        if total!=len(chunks):raise ValueError("Vínculos relacionais incompletos; atualização revertida.")
    resultado['vinculos_relacionais_atualizados']=vinculados
    return resultado


def remover(material_id, store=None):
    store = store or VectorStore()
    with store._conectar() as c:
        c.execute("SET LOCAL statement_timeout='15s'")
        result = c.execute("DELETE FROM chunk_documento WHERE COALESCE(material_id,(metadata->>'material_id')::bigint)=%s", [material_id])
        return {"removidos":result.rowcount}
