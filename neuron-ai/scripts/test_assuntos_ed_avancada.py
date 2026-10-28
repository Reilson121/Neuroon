import sys
from pathlib import Path

from app.rag.assunto_processor import AssuntoProcessor
from app.rag.mapas.estrutura_de_dados_avancada import MAPA


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PASTA = Path(
    "materiais_academicos/periodo_03/estrutura_de_dados_avancada"
)

# Uso:
#   python -m scripts.test_assuntos_ed_avancada Aula_0.pdf
#   python -m scripts.test_assuntos_ed_avancada Aula_0.pdf Aula_1.pdf
arquivos = sys.argv[1:] or ["Aula_0.pdf"]

ARQUIVO_SAIDA = Path(
    "saidas_testes/estrutura_de_dados_avancada_"
    + "_".join(a.replace(".pdf", "").lower() for a in arquivos)
    + ".json"
)

print("=" * 80)
print("INGESTÃO POR ASSUNTO - ESTRUTURA DE DADOS AVANÇADA")
print("=" * 80)
print(f"Arquivos: {arquivos}")
print("ATENÇÃO: páginas multimodais podem chamar o OpenRouter.")

processor = AssuntoProcessor(chunk_size=1000, chunk_overlap=150)

resultado = processor.processar_disciplina(
    pasta=PASTA, mapa=MAPA, arquivos=arquivos
)

processor.salvar_json(resultado, ARQUIVO_SAIDA)

print("\n" + "=" * 80)
print("RESUMO POR ARQUIVO")
print("=" * 80)
for r in resultado["arquivos"]:
    print(
        f"{r['arquivo']}: {r['paginas_indexadas']}/"
        f"{r['total_paginas_pdf']} páginas indexadas, "
        f"{r['total_chunks']} chunks"
    )

print("\n" + "=" * 80)
print("RESUMO POR ASSUNTO")
print("=" * 80)
for assunto, item in resultado["por_assunto"].items():
    print(
        f"{assunto:32s} páginas={item['paginas']:3d} "
        f"multimodais={item['multimodais']:2d} chunks={item['chunks']:3d}"
    )

print("\n" + "=" * 80)
print("AMOSTRA DE METADADOS (3 primeiros chunks)")
print("=" * 80)
for chunk in resultado["chunks"][:3]:
    m = chunk["metadata"]
    print(
        f"\n{chunk['chunk_id']} | assunto={m['assunto']} | "
        f"aula={m['aula']} | arquivo={m['arquivo']} | "
        f"pag={m['pagina']} | {m['tipo_extracao']} | "
        f"chunk={m['chunk_index']}"
    )
    print(chunk["conteudo"][:250])

print(f"\nTotal de chunks: {resultado['total_chunks']}")
print(f"Salvo em: {ARQUIVO_SAIDA}")
