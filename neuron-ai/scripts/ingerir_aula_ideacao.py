"""Ingestão retomável de Ideação. Páginas visuais são enviadas ao OpenRouter."""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from types import SimpleNamespace

from app.rag.ideacao_corpus import (
    AULAS, DISCIPLINA, PERIODO, RAIZ, localizar_pdf, salvar_json, sha256, validar_aula,
)


def processar_aula(codigo, limite=None):
    import pymupdf
    from openai import OpenAI
    from app.rag.chunk_processor import ChunkProcessor
    from app.rag.document_processor import DocumentProcessor

    pdf = localizar_pdf(codigo)
    pdf_hash = sha256(pdf.read_bytes())
    saida = RAIZ / f"saidas_testes/ideacao_aula_{codigo}_pipeline_completa.json"
    checkpoint = RAIZ / f"saidas_testes/ideacao_aula_{codigo}_checkpoint.json"
    processor = DocumentProcessor()
    if not processor.api_key or not processor.vision_model:
        raise ValueError("Configure o provedor visual do projeto.")
    identidade = {"pdf_sha256": pdf_hash, "modelo_visual": processor.vision_model,
                  "versao_extracao": 1, "disciplina": DISCIPLINA, "aula": codigo}
    estado = {**identidade, "paginas": []}
    if checkpoint.exists():
        estado = json.loads(checkpoint.read_text(encoding="utf-8"))
        if any(estado.get(k) != v for k, v in identidade.items()):
            raise ValueError("Checkpoint pertence a outra versão; preserve-o e revise antes de refazer.")
    with pymupdf.open(pdf) as doc:
        if saida.exists():
            validar_aula(json.loads(saida.read_text(encoding="utf-8")), codigo, pdf.name, len(doc), pdf_hash)
            print(f"Aula {codigo}: saída completa já existente; nenhuma chamada.", flush=True)
            return codigo
        paginas = {p["metadata"]["pagina"]: p for p in estado["paginas"]}
        if len(paginas) != len(estado["paginas"]) or any(n not in range(1, len(doc)+1) for n in paginas):
            raise ValueError("Checkpoint com páginas inválidas.")
        with OpenAI(base_url="https://openrouter.ai/api/v1", api_key=processor.api_key,
                    timeout=75.0, max_retries=1) as cliente:
            def criar(**kwargs):
                resposta = cliente.chat.completions.create(**kwargs)
                if not resposta.choices or resposta.choices[0].finish_reason != "stop":
                    raise RuntimeError("Extração visual incompleta; página não salva.")
                return resposta
            processor.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=criar)))
            for numero, pagina in enumerate(doc, 1):
                if numero in paginas:
                    continue
                if limite is not None and numero > limite:
                    break
                texto = processor.extrair_texto_pagina(pagina)
                analise = processor.precisa_multimodal(pagina, texto)
                # Os quadros das páginas 3 e 4 de Histórias estão em imagens,
                # embora o título da página 4 ultrapasse o detector automático.
                visual = analise["precisa_multimodal"] or (codigo == "03" and numero in {3, 4})
                conteudo = processor.analisar_pagina_visual(pagina) if visual else texto
                if not conteudo.strip():
                    raise ValueError(f"Aula {codigo}, página {numero}: extração vazia.")
                paginas[numero] = {"conteudo": conteudo, "metadata": {
                    "periodo": PERIODO, "disciplina": DISCIPLINA, "aula": codigo,
                    "assunto": AULAS[codigo][1], "arquivo": pdf.name,
                    "pasta_aula": AULAS[codigo][0], "pagina": numero,
                    "tipo_arquivo": "pdf", "tipo_extracao": "multimodal" if visual else "textual",
                    "caracteres_texto_original": len(texto),
                    "motivos_deteccao": analise["motivos"],
                    **({"modelo_visual": processor.vision_model} if visual else {}),
                }}
                estado["paginas"] = [paginas[n] for n in sorted(paginas)]
                salvar_json(checkpoint, estado)
                print(f"Aula {codigo}: página {numero}/{len(doc)} salva.", flush=True)
        if len(paginas) != len(doc):
            return codigo
        lista = [paginas[n] for n in sorted(paginas)]
        chunks = ChunkProcessor(chunk_size=1000, chunk_overlap=150).processar_resultados(lista)
        resumo = {"periodo": PERIODO, "disciplina": DISCIPLINA, "aula": codigo,
                  "assunto": AULAS[codigo][1], "arquivo": pdf.name, "pdf_sha256": pdf_hash,
                  "modelo_visual": processor.vision_model, "total_paginas": len(doc),
                  "total_chunks": len(chunks), "chunk_size": 1000, "chunk_overlap": 150,
                  "paginas_multimodais": sum(p["metadata"]["tipo_extracao"] == "multimodal" for p in lista)}
        resumo["paginas_textuais"] = len(doc) - resumo["paginas_multimodais"]
        dados = {"resumo": resumo, "paginas": lista, "chunks": chunks}
        validar_aula(dados, codigo, pdf.name, len(doc), pdf_hash)
        salvar_json(saida, dados)
        print(f"Aula {codigo}: concluída, {len(chunks)} chunks.", flush=True)
    return codigo


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aula", choices=[*AULAS, "todas"])
    parser.add_argument("--processos", type=int, choices=range(1, 4), default=1)
    parser.add_argument("--limite-paginas", type=int, choices=range(1, 1000))
    args = parser.parse_args(argv)
    codigos = list(AULAS) if args.aula == "todas" else [args.aula]
    if args.processos == 1:
        for codigo in codigos:
            processar_aula(codigo, args.limite_paginas)
    else:
        # PyMuPDF não é usado por threads: cada aula tem seu próprio processo.
        with ProcessPoolExecutor(max_workers=args.processos) as pool:
            tarefas = [pool.submit(processar_aula, c, args.limite_paginas) for c in codigos]
            for tarefa in tarefas:
                tarefa.result()
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except Exception as erro:
        print(f"Ingestão interrompida ({type(erro).__name__}); progresso salvo por página.", file=sys.stderr)
        sys.exit(1)
