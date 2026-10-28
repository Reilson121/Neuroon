"""Corpus de Design: consolidação local, rastreável e sem chamadas de visão."""

import copy
import hashlib
import json
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
DISCIPLINA = "design_de_artefatos_digitais"
PERIODO = "03"
JSON_CHUNKS = RAIZ / "saidas_testes/design_de_artefatos_digitais_completa.json"
REVISOES = RAIZ / "app/rag/mapas/design_revisoes.json"
AULAS = {
    "01": ("aula_01_introducao_ao_design", "introducao_ao_design"),
    "02": ("aula_02_ferramentas_visuais", "ferramentas_visuais"),
    "03": ("aula_03_publico_alvo", "publico_alvo"),
    "04": ("aula_04_comportamento_do_consumidor", "comportamento_do_consumidor"),
    "05": ("aula_05_design_de_interface", "design_de_interface"),
    "06": ("aula_06_principios_de_design", "principios_de_design"),
    "07": ("aula_07_design_de_interface_diagramacao", "design_de_interface_diagramacao"),
    "08": ("aula_08_design_thinking", "design_thinking"),
    "complementar": ("material_complementar_matriz_csd", "matriz_csd"),
}


def sha256(conteudo):
    return hashlib.sha256(conteudo).hexdigest()


def validar_aula(dados, codigo, assunto, arquivo, total_paginas):
    """Exige todas as páginas uma única vez e identidade consistente."""
    paginas = dados["paginas"]
    numeros = [p["metadata"]["pagina"] for p in paginas]
    if sorted(numeros) != list(range(1, total_paginas + 1)):
        raise ValueError(f"Aula {codigo}: páginas ausentes, repetidas ou fora do PDF.")
    identidade = {
        "periodo": PERIODO, "disciplina": DISCIPLINA,
        "aula": codigo, "assunto": assunto, "arquivo": arquivo,
    }
    if any(dados["resumo"].get(k) != v for k, v in identidade.items()):
        raise ValueError(f"Aula {codigo}: resumo de outra origem.")
    if dados["resumo"]["total_paginas"] != total_paginas:
        raise ValueError(f"Aula {codigo}: resumo desatualizado.")
    for pagina in paginas:
        m = pagina["metadata"]
        if any(m.get(k) != v for k, v in identidade.items()):
            raise ValueError(f"Aula {codigo}: metadados de outra origem.")
        if m.get("tipo_extracao") not in {"textual", "multimodal"}:
            raise ValueError(f"Aula {codigo}: tipo de extração inválido.")
        if not pagina["conteudo"].strip():
            raise ValueError(f"Aula {codigo}, página {m['pagina']}: conteúdo vazio.")


def consolidar(raiz=RAIZ, revisoes_path=REVISOES):
    import pymupdf
    from app.rag.chunk_processor import ChunkProcessor

    raiz = Path(raiz)
    revisoes = json.loads(Path(revisoes_path).read_text(encoding="utf-8"))
    correcoes = {(r["aula"], r["pagina"]): r for r in revisoes["paginas"]}
    if len(correcoes) != len(revisoes["paginas"]):
        raise ValueError("Há revisões duplicadas para uma página.")
    aplicadas = set()
    paginas, arquivos = [], []
    splitter = ChunkProcessor(chunk_size=1000, chunk_overlap=150)
    for codigo, (pasta, assunto) in AULAS.items():
        origem = raiz / f"saidas_testes/design_aula_{codigo}_pipeline_completa.json"
        pdfs = list((raiz / "materiais_academicos/periodo_03" / DISCIPLINA / pasta).glob("*.pdf"))
        if len(pdfs) != 1:
            raise ValueError(f"Aula {codigo}: esperado exatamente um PDF.")
        pdf = pdfs[0]
        pdf_hash = sha256(pdf.read_bytes())
        dados = json.loads(origem.read_text(encoding="utf-8"))
        with pymupdf.open(pdf) as documento:
            total = len(documento)
        validar_aula(dados, codigo, assunto, pdf.name, total)
        aula_paginas = copy.deepcopy(sorted(dados["paginas"], key=lambda p: p["metadata"]["pagina"]))
        limpezas = []
        for pagina in aula_paginas:
            numero = pagina["metadata"]["pagina"]
            correcao = correcoes.get((codigo, numero))
            if correcao is not None:
                if (correcao["pdf_sha256"] != pdf_hash or
                        correcao["conteudo_anterior_sha256"] != sha256(pagina["conteudo"].encode("utf-8"))):
                    raise ValueError(f"Aula {codigo}, página {numero}: revisão pertence a outra versão.")
                pagina["conteudo"] = correcao["conteudo"]
                pagina["metadata"]["revisao_visual"] = correcao["motivo"]
                contexto = correcao.get("paginas_contexto", [])
                if any(type(n) is not int or not 1 <= n <= total or n == numero for n in contexto):
                    raise ValueError("Página de contexto fora do PDF.")
                if contexto:
                    pagina["metadata"]["paginas_mescladas"] = sorted(set(contexto))
                aplicadas.add((codigo, numero))
            # O PostgreSQL não aceita NUL em TEXT. Não remove símbolos acadêmicos.
            if "\x00" in pagina["conteudo"]:
                pagina["conteudo"] = pagina["conteudo"].replace("\x00", "")
                pagina["metadata"]["nul_removido"] = True
                limpezas.append(numero)
            if not pagina["conteudo"].strip():
                raise ValueError(f"Aula {codigo}, página {numero}: revisão vazia.")
        chunks = splitter.processar_resultados(aula_paginas)
        arquivos.append({
            "aula": codigo, "assunto": assunto, "arquivo": pdf.name,
            "pdf": pdf.relative_to(raiz).as_posix(), "pdf_sha256": pdf_hash,
            "json_origem": origem.relative_to(raiz).as_posix(),
            "json_origem_sha256": sha256(origem.read_bytes()),
            "paginas": total, "chunks": len(chunks),
            "paginas_revisadas": sorted(n for c, n in aplicadas if c == codigo),
            "paginas_com_nul_removido": limpezas,
        })
        paginas.extend(aula_paginas)
    if aplicadas != correcoes.keys():
        raise ValueError("Há revisões para páginas ou aulas inexistentes.")
    chunks = splitter.processar_resultados(paginas)
    if len({c["chunk_id"] for c in chunks}) != len(chunks):
        raise ValueError("IDs de chunks duplicados.")
    cobertura = {(c["metadata"]["aula"], c["metadata"]["pagina"]) for c in chunks}
    if len(cobertura) != len(paginas):
        raise ValueError("Há páginas sem chunks.")
    return {
        "versao": 1, "disciplina": DISCIPLINA, "periodo": PERIODO,
        "total_aulas": len(arquivos), "total_paginas": len(paginas),
        "total_chunks": len(chunks), "total_paginas_revisadas": len(aplicadas),
        "chunk_size": 1000, "chunk_overlap": 150,
        "revisoes_sha256": sha256(Path(revisoes_path).read_bytes()),
        "arquivos": arquivos, "paginas": paginas, "chunks": chunks,
    }


def carregar_validado():
    """Impede uso de um consolidado que não corresponde mais às fontes locais."""
    salvo = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))
    if salvo != consolidar():
        raise ValueError("Corpus desatualizado. Execute scripts.preparar_design.")
    return salvo


def preparar_material(material, assuntos):
    """Vincula somente o PDF conferido ao catálogo, preservando texto e IDs."""
    if (material.get('disciplina_slug') != DISCIPLINA or material['tipo'] != 'SLIDE_AULA'
            or material['periodo_numero'] != 3):
        raise ValueError('Material não preparado para Design de Artefatos Digitais.')
    if not all(material[k] for k in ('ativo', 'disciplina_ativa', 'periodo_ativo', 'fonte_monitor_virtual')):
        raise ValueError('Fonte indisponível no catálogo.')
    dados = carregar_validado()
    origem = next((a for a in dados['arquivos']
                   if material['referencia_externa'] == 'local:' + a['pdf']), None)
    if origem is None:
        raise ValueError('Origem não preparada para Design de Artefatos Digitais.')
    chunks = copy.deepcopy([c for c in dados['chunks']
                            if c['metadata']['arquivo'] == origem['arquivo']
                            and c['metadata']['aula'] == origem['aula']])
    for chunk in chunks:
        meta = chunk['metadata']
        assunto = assuntos.get(meta['assunto'])
        if (not assunto or not assunto['ativo'] or assunto['disciplina_id'] != material['disciplina_id']
                or meta['assunto'] != origem['assunto'] or meta['disciplina'] != DISCIPLINA
                or material['assunto_id'] != assunto['id']):
            raise ValueError('Assunto indisponível ou incompatível com o material.')
        meta.update(material_id=material['id'], disciplina_id=material['disciplina_id'],
                    periodo_id=material['periodo_id'], assunto_id=assunto['id'],
                    titulo_material=material['titulo'], tipo_material='SLIDE_AULA',
                    fonte_monitor_virtual=True, disponivel_para_pratica=False,
                    autorizacao_professor=material['autorizacao_professor'])
    return chunks
