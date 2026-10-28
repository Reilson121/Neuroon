"""Identidade e conferência do corpus teórico de Estatística.

A extração e o chunking continuam nos processadores existentes.
"""

import hashlib
import json
import copy
from collections import Counter
from pathlib import Path

from app.rag.mapas.estatistica import MAPA, ORDEM_ASSUNTOS

RAIZ = Path(__file__).resolve().parents[2]
DISCIPLINA = MAPA["disciplina"]
PERIODO = MAPA["periodo"]
PASTA = RAIZ / "materiais_academicos/periodo_03/estatistica"
ARQUIVO = "estatistica_novo.pdf"
PDF = PASTA / ARQUIVO
JSON_CHUNKS = RAIZ / "saidas_testes/estatistica_completa.json"
CHECKPOINT = RAIZ / "saidas_testes/estatistica_checkpoint.json"
REVISOES = RAIZ / "app/rag/mapas/estatistica_revisoes.json"


def sha256(conteudo):
    return hashlib.sha256(conteudo).hexdigest()


def mapa_sha256():
    return sha256(json.dumps(MAPA, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def salvar_json(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporario.replace(caminho)


def enriquecer(dados, documento, pdf_hash):
    """Acrescenta proveniência antes de refazer os chunks pelo componente comum."""
    from app.rag.chunk_processor import ChunkProcessor

    revisoes = json.loads(REVISOES.read_text(encoding="utf-8"))
    if revisoes["pdf_sha256"] != pdf_hash:
        raise ValueError("Revisões de outra versão do PDF.")
    dados.update(pdf_sha256=pdf_hash, mapa_sha256=mapa_sha256(),
                 revisoes_sha256=sha256(REVISOES.read_bytes()),
                 total_paginas_pdf=len(documento), ordem_assuntos=list(ORDEM_ASSUNTOS))
    for pagina in dados["paginas"]:
        aplicar_revisoes(pagina, revisoes)
        pagina["metadata"].update({
            "pdf_sha256": pdf_hash, "mapa_sha256": mapa_sha256(),
            "tipo_material": "SLIDE_AULA", "titulo_material": "Estatística — slides consolidados",
            "metadados_documento_originais": documento.metadata,
        })
    dados["chunks"] = ChunkProcessor(chunk_size=1000, chunk_overlap=150).processar_resultados(dados["paginas"])
    dados["total_chunks"] = len(dados["chunks"])
    contagem_chunks = Counter(c["metadata"]["assunto"] for c in dados["chunks"])
    dados["por_assunto"] = {}
    for assunto in ORDEM_ASSUNTOS:
        paginas = [p for p in dados["paginas"] if p["metadata"]["assunto"] == assunto]
        if paginas:
            dados["por_assunto"][assunto] = {
                "paginas": len(paginas), "chunks": contagem_chunks[assunto],
                "multimodais": sum(p["metadata"]["tipo_extracao"] == "multimodal" for p in paginas),
                "paginas_origem": sum(1 + len(p["metadata"].get("paginas_mescladas", [])) for p in paginas),
            }
    for arquivo in dados.get("arquivos", []):
        arquivo["total_chunks"] = len(dados["chunks"])
    return dados


def aplicar_revisoes(pagina, revisoes):
    m = pagina["metadata"]
    m.pop("revisoes_ia", None)
    m.pop("revisao_oficial_professor", None)
    numeros = sorted([m["pagina"], *m.get("paginas_mescladas", [])])
    notas = [{"pagina": n, "texto": revisoes["paginas"][str(n)]}
             for n in numeros if str(n) in revisoes["paginas"]]
    original = pagina.get("conteudo_original", pagina["conteudo"])
    extracao = revisoes.get("extracoes", {}).get(str(m["pagina"]))
    if extracao:
        if original != extracao["conteudo"]:
            if sha256(original.encode("utf-8")) != extracao["conteudo_extraido_anterior_sha256"]:
                raise ValueError("Correção de extração pertence a outro texto.")
            pagina["conteudo_extraido_automaticamente"] = original
            original = extracao["conteudo"]
        automatico = pagina.get("conteudo_extraido_automaticamente")
        if automatico is not None and sha256(automatico.encode("utf-8")) != extracao["conteudo_extraido_anterior_sha256"]:
            raise ValueError("Texto automático preservado diverge da revisão visual.")
        m["revisao_extracao_visual"] = extracao["motivo"]
    pagina["conteudo_original"] = original
    pagina["conteudo"] = original
    if notas:
        m["revisoes_ia"] = notas
        m["revisao_oficial_professor"] = False
        pagina["conteudo"] += "\n\n" + "\n\n".join(
            f"Observação de revisão por IA (não é gabarito oficial do professor), página {n['pagina']}: {n['texto']}"
            for n in notas)


def validar_corpus(dados, pdf=PDF):
    import pymupdf
    from app.rag.assunto_processor import AssuntoProcessor
    from app.rag.chunk_processor import ChunkProcessor

    with pymupdf.open(pdf) as documento:
        total = len(documento)
        originais = documento.metadata
    pdf_hash = sha256(Path(pdf).read_bytes())
    revisoes = json.loads(REVISOES.read_text(encoding="utf-8"))
    if dados.get("revisoes_sha256") != sha256(REVISOES.read_bytes()) or revisoes["pdf_sha256"] != pdf_hash:
        raise ValueError("Revisões ausentes ou desatualizadas.")
    config = MAPA["arquivos"][ARQUIVO]
    esperado = AssuntoProcessor().validar_arquivo(ARQUIVO, config, total)
    identidade = {"periodo": PERIODO, "disciplina": DISCIPLINA,
                  "pdf_sha256": pdf_hash, "mapa_sha256": mapa_sha256()}
    if any(dados.get(k) != v for k, v in identidade.items()):
        raise ValueError("Corpus de outro mapa, PDF ou disciplina.")
    if dados.get("total_paginas_pdf") != total or dados.get("ordem_assuntos") != list(ORDEM_ASSUNTOS):
        raise ValueError("Documento ou ordem de navegação divergente.")
    paginas = dados["paginas"]
    vistas = []
    for item in paginas:
        m = item["metadata"]
        numeros = [m["pagina"], *m.get("paginas_mescladas", [])]
        if len(set(numeros)) != len(numeros) or any(esperado.get(n) != m.get("assunto") for n in numeros):
            raise ValueError("Página fora do assunto aprovado ou mesclagem entre assuntos.")
        vistas.extend(numeros)
        conferido = copy.deepcopy(item)
        if "conteudo_original" not in item:
            raise ValueError("Texto original não preservado.")
        aplicar_revisoes(conferido, revisoes)
        if conferido != item:
            raise ValueError("Revisão alterada ou misturada ao texto original.")
        if any(m.get(k) != v for k, v in identidade.items()):
            raise ValueError("Metadados de outra origem.")
        if (m.get("arquivo") != ARQUIVO or m.get("aula") is not None or
                m.get("tipo_arquivo") != "pdf" or m.get("tipo_material") != "SLIDE_AULA" or
                m.get("metadados_documento_originais") != originais):
            raise ValueError("Identidade ou metadados documentais divergentes.")
        metodo = "multimodal" if m["pagina"] in config["paginas_multimodais"] else "textual"
        if m.get("tipo_extracao") != metodo:
            raise ValueError("Método divergente do mapa aprovado; revisar fallback antes de indexar.")
        if not isinstance(item["conteudo"], str) or not item["conteudo"].strip() or "\x00" in item["conteudo"]:
            raise ValueError("Conteúdo vazio ou inválido.")
    if Counter(vistas) != Counter(esperado.keys()):
        raise ValueError("Cobertura incompleta ou páginas repetidas.")
    chunks = dados["chunks"]
    if dados.get("total_chunks") != len(chunks) or len({c["chunk_id"] for c in chunks}) != len(chunks):
        raise ValueError("Contagem ou IDs de chunks inválidos.")
    regenerados = ChunkProcessor(chunk_size=1000, chunk_overlap=150).processar_resultados(paginas)
    if chunks != regenerados:
        raise ValueError("Chunks não correspondem às páginas e metadados conferidos.")
    if {p["metadata"]["pagina"] for p in paginas} != {c["metadata"]["pagina"] for c in chunks}:
        raise ValueError("Página sem chunks.")
    return {"disciplina": DISCIPLINA, "assuntos": len(ORDEM_ASSUNTOS),
            "paginas_pdf": total, "paginas_cobertas": len(vistas),
            "paginas_apos_mesclagem": len(paginas), "chunks": len(chunks),
            "chunks_por_assunto": dict(Counter(c["metadata"]["assunto"] for c in chunks))}


def carregar_validado():
    dados = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))
    validar_corpus(dados)
    return dados
