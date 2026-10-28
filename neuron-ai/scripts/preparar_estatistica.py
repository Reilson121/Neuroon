"""Processa o mapa aprovado reutilizando os componentes de RAG existentes.

O modo plano é local. Amostra e processar podem chamar o modelo visual
configurado; o checkpoint evita repetir extrações já concluídas.
"""

import argparse
import copy
import json
import sys
from types import SimpleNamespace

from app.rag.estatistica_corpus import (
    ARQUIVO, CHECKPOINT, DISCIPLINA, JSON_CHUNKS, MAPA, PASTA, PDF, PERIODO,
    RAIZ, enriquecer, mapa_sha256, salvar_json, sha256, validar_corpus,
)

AMOSTRA = [14, 40, 51, 53, 77]


def mapa_parcial(numeros):
    mapa = copy.deepcopy(MAPA)
    c = mapa["arquivos"][ARQUIVO]
    c["assuntos"] = {s: [(n, n) for n in numeros if any(a <= n <= b for a, b in faixas)]
                     for s, faixas in c["assuntos"].items()}
    c["assuntos"] = {s: faixas for s, faixas in c["assuntos"].items() if faixas}
    for chave in ("paginas_textuais", "paginas_multimodais"):
        c[chave] = [n for n in c[chave] if n in numeros]
    return mapa


def executar(modo):
    import pymupdf
    from app.rag.assunto_processor import AssuntoProcessor

    processor = AssuntoProcessor(chunk_size=1000, chunk_overlap=150)
    config = MAPA["arquivos"][ARQUIVO]
    plano = processor.planejar_arquivo(PASTA, ARQUIVO, config)
    if modo == "plano":
        salvar_json(RAIZ / "saidas_testes/estatistica_plano.json", plano)
        print(json.dumps({"disciplina": DISCIPLINA, "paginas": len(plano),
                          "mapeadas": sum(p["assunto"] is not None for p in plano),
                          "multimodais": sum(p["metodo"] == "multimodal" for p in plano)}, ensure_ascii=False))
        return
    if modo == "verificar":
        dados = json.loads(JSON_CHUNKS.read_text(encoding="utf-8"))
        print(json.dumps(validar_corpus(dados), ensure_ascii=False, indent=2))
        return
    if modo == "textual":
        dados = processor.processar_disciplina(PASTA, mapa_parcial(config["paginas_textuais"]))
        with pymupdf.open(PDF) as documento:
            enriquecer(dados, documento, sha256(PDF.read_bytes()))
        dados["status"] = "previa_parcial_nao_indexavel"
        salvar_json(RAIZ / "saidas_testes/estatistica_textual_previa.json", dados)
        print(f"Prévia local: {len(dados['paginas'])} páginas após mesclagem; {len(dados['chunks'])} chunks. Não indexada.")
        return
    from openai import OpenAI

    visual = processor.document_processor
    identidade = {"pdf_sha256": sha256(PDF.read_bytes()), "mapa_sha256": mapa_sha256(),
                  "modelo_visual": visual.vision_model, "versao": 1}
    estado = {**identidade, "paginas_visuais": {}}
    if CHECKPOINT.exists():
        estado = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        if any(estado.get(k) != v for k, v in identidade.items()):
            raise ValueError("Checkpoint de outra versão. Preservar e revisar antes de refazer.")
    for numero, item in estado["paginas_visuais"].items():
        if (int(numero) not in config["paginas_multimodais"] or
                sha256(item["conteudo"].encode("utf-8")) != item["conteudo_sha256"]):
            raise ValueError("Página de checkpoint inválida.")
    if not visual.api_key or not visual.vision_model:
        raise ValueError("Provedor visual não configurado.")
    mapa = mapa_parcial(AMOSTRA) if modo == "amostra" else copy.deepcopy(MAPA)

    extrair_original = visual.analisar_pagina_visual
    pagina_atual = {"numero": None}
    with OpenAI(base_url="https://openrouter.ai/api/v1", api_key=visual.api_key,
                timeout=75.0, max_retries=1) as cliente:
        def criar(**kwargs):
            # Tabelas estatísticas densas precisam de espaço para transcrever
            # as células. O processador comum mantém seu limite original.
            if pagina_atual["numero"] in {85, 93, 106, 119}:
                kwargs["max_tokens"] = 12000
            resposta = cliente.chat.completions.create(**kwargs)
            if not resposta.choices or resposta.choices[0].finish_reason != "stop":
                salvar_json(RAIZ / "saidas_testes/estatistica_falha_visual.json", {
                    "pagina": pagina_atual["numero"],
                    "finish_reason": resposta.choices[0].finish_reason if resposta.choices else None,
                    "usage": resposta.usage.model_dump() if resposta.usage else None,
                })
                raise RuntimeError("Extração visual incompleta; página não salva.")
            return resposta

        visual.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=criar)))

        def extrair_com_checkpoint(pagina):
            numero = str(pagina.number + 1)
            if numero in estado["paginas_visuais"]:
                return estado["paginas_visuais"][numero]["conteudo"]
            pagina_atual["numero"] = int(numero)
            conteudo = extrair_original(pagina)
            if not conteudo.strip():
                raise ValueError("Extração visual vazia; revisar antes de prosseguir.")
            estado["paginas_visuais"][numero] = {
                "conteudo": conteudo, "conteudo_sha256": sha256(conteudo.encode("utf-8"))}
            salvar_json(CHECKPOINT, estado)
            print(f"Estatística: página {numero} salva; "
                  f"{len(estado['paginas_visuais'])}/{len(config['paginas_multimodais'])} visuais concluídas.", flush=True)
            return conteudo

        visual.analisar_pagina_visual = extrair_com_checkpoint
        dados = processor.processar_disciplina(PASTA, mapa)
    for pagina in dados["paginas"]:
        if pagina["metadata"]["tipo_extracao"] == "multimodal":
            pagina["metadata"]["modelo_visual"] = visual.vision_model
    with pymupdf.open(PDF) as documento:
        enriquecer(dados, documento, identidade["pdf_sha256"])
    if modo == "amostra":
        dados["status"] = "previa_parcial_nao_indexavel"
        salvar_json(RAIZ / "saidas_testes/estatistica_amostra.json", dados)
        print(f"Amostra salva: {len(dados['paginas'])} páginas, {len(dados['chunks'])} chunks.")
    else:
        resumo = validar_corpus(dados)
        salvar_json(JSON_CHUNKS, dados)
        salvar_json(RAIZ / "saidas_testes/estatistica_validacao_corpus.json", resumo)
        print(json.dumps(resumo, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modo", choices=["plano", "textual", "amostra", "processar", "verificar"])
    executar(parser.parse_args(argv).modo)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except Exception as erro:
        print(f"Processamento interrompido ({type(erro).__name__}); confira configuração e checkpoint.", file=sys.stderr)
        sys.exit(1)
