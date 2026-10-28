"""Corpus rastreável das cinco aulas de Projeto de Ideação de Software."""

import copy
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DISCIPLINA = "projeto_de_ideacao_de_software"
PERIODO = "03"
JSON_CHUNKS = RAIZ / "saidas_testes/projeto_de_ideacao_de_software_completa.json"
REVISOES = RAIZ / "app/rag/mapas/ideacao_revisoes.json"
AULAS = {
    "01": ("aula_01_introducao", "introducao"),
    "02": ("aula_02_lean_canvas", "lean_canvas"),
    "03": ("aula_03_historias_de_usuario", "historias_de_usuario"),
    "04": ("aula_04_mapa_de_navegacao_e_wireframe", "mapa_de_navegacao_e_wireframe"),
    "05": ("aula_05_matriz_csd", "matriz_csd"),
}


def sha256(conteudo):
    return hashlib.sha256(conteudo).hexdigest()


def localizar_pdf(codigo, raiz=RAIZ):
    pasta = Path(raiz) / "materiais_academicos/periodo_03" / DISCIPLINA / AULAS[codigo][0]
    pdfs = sorted(pasta.glob("*.pdf"))
    if len(pdfs) != 1:
        raise ValueError(f"Aula {codigo}: esperado exatamente um PDF.")
    return pdfs[0]


def validar_aula(dados, codigo, arquivo, total_paginas, pdf_hash):
    identidade = dict(periodo=PERIODO, disciplina=DISCIPLINA, aula=codigo,
                      assunto=AULAS[codigo][1], arquivo=arquivo)
    resumo = dados["resumo"]
    if any(resumo.get(k) != v for k, v in identidade.items()):
        raise ValueError(f"Aula {codigo}: resumo de outra origem.")
    if resumo.get("pdf_sha256") != pdf_hash or resumo.get("total_paginas") != total_paginas:
        raise ValueError(f"Aula {codigo}: PDF de outra versão.")
    numeros = [p["metadata"]["pagina"] for p in dados["paginas"]]
    if sorted(numeros) != list(range(1, total_paginas + 1)):
        raise ValueError(f"Aula {codigo}: páginas ausentes, repetidas ou fora do PDF.")
    for pagina in dados["paginas"]:
        m = pagina["metadata"]
        if any(m.get(k) != v for k, v in identidade.items()):
            raise ValueError(f"Aula {codigo}: metadados de outra origem.")
        if m.get("tipo_arquivo") != "pdf" or m.get("tipo_extracao") not in {"textual", "multimodal"}:
            raise ValueError(f"Aula {codigo}: extração inválida.")
        if not isinstance(pagina["conteudo"], str) or not pagina["conteudo"].strip():
            raise ValueError(f"Aula {codigo}: página vazia.")


def consolidar(raiz=RAIZ, revisoes_path=REVISOES):
    import pymupdf
    from app.rag.chunk_processor import ChunkProcessor

    raiz = Path(raiz)
    revisoes = json.loads(Path(revisoes_path).read_text(encoding="utf-8"))
    correcoes = {(r["aula"], r["pagina"]): r for r in revisoes["paginas"]}
    if len(correcoes) != len(revisoes["paginas"]):
        raise ValueError("Há revisões duplicadas para uma página.")
    aplicadas, paginas, arquivos = set(), [], []
    splitter = ChunkProcessor(chunk_size=1000, chunk_overlap=150)
    for codigo, (_, assunto) in AULAS.items():
        pdf = localizar_pdf(codigo, raiz)
        pdf_hash = sha256(pdf.read_bytes())
        origem = raiz / f"saidas_testes/ideacao_aula_{codigo}_pipeline_completa.json"
        dados = json.loads(origem.read_text(encoding="utf-8"))
        with pymupdf.open(pdf) as doc:
            total = len(doc)
        validar_aula(dados, codigo, pdf.name, total, pdf_hash)
        aula_paginas = copy.deepcopy(sorted(dados["paginas"], key=lambda p: p["metadata"]["pagina"]))
        for pagina in aula_paginas:
            numero = pagina["metadata"]["pagina"]
            correcao = correcoes.get((codigo, numero))
            if correcao is not None:
                if (correcao["pdf_sha256"] != pdf_hash or
                        correcao["conteudo_anterior_sha256"] != sha256(pagina["conteudo"].encode("utf-8"))):
                    raise ValueError(f"Aula {codigo}, página {numero}: revisão de outra versão.")
                pagina["conteudo"] = correcao["conteudo"]
                pagina["metadata"]["revisao_visual"] = correcao["motivo"]
                aplicadas.add((codigo, numero))
            if "\x00" in pagina["conteudo"]:
                pagina["conteudo"] = pagina["conteudo"].replace("\x00", "")
                pagina["metadata"]["nul_removido"] = True
            if not pagina["conteudo"].strip():
                raise ValueError("Revisão vazia.")
        arquivos.append({
            "aula": codigo, "assunto": assunto, "arquivo": pdf.name,
            "pdf": pdf.relative_to(raiz).as_posix(), "pdf_sha256": pdf_hash,
            "json_origem": origem.relative_to(raiz).as_posix(),
            "json_origem_sha256": sha256(origem.read_bytes()),
            "paginas": total, "chunks": len(splitter.processar_resultados(aula_paginas)),
            "paginas_revisadas": sorted(n for c, n in aplicadas if c == codigo),
        })
        paginas.extend(aula_paginas)
    if aplicadas != correcoes.keys():
        raise ValueError("Há revisões para páginas ou aulas inexistentes.")
    chunks = splitter.processar_resultados(paginas)
    if len({c["chunk_id"] for c in chunks}) != len(chunks):
        raise ValueError("IDs de chunks duplicados.")
    if {(p["metadata"]["aula"], p["metadata"]["pagina"]) for p in paginas} != {
        (c["metadata"]["aula"], c["metadata"]["pagina"]) for c in chunks
    }:
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
    salvo = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))
    if salvo != consolidar():
        raise ValueError("Corpus desatualizado. Execute scripts.preparar_ideacao.")
    return salvo


def salvar_json(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    if not caminho.exists() or caminho.read_text(encoding="utf-8") != texto:
        temporario = caminho.with_suffix(".tmp")
        temporario.write_text(texto, encoding="utf-8")
        temporario.replace(caminho)
