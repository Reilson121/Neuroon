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

print("=" * 80)
print("PLANO DE INGESTÃO POR ASSUNTO (NÃO CHAMA API)")
print("=" * 80)

processor = AssuntoProcessor()

total_api = 0

for nome, config in MAPA["arquivos"].items():

    linhas = processor.planejar_arquivo(PASTA, nome, config)

    print(f"\n### {nome}")

    assuntos = {}
    for linha in linhas:
        if linha["assunto"] is None:
            continue
        item = assuntos.setdefault(
            linha["assunto"], {"paginas": 0, "multimodais": []}
        )
        item["paginas"] += 1
        if linha["metodo"] == "multimodal":
            item["multimodais"].append(linha["pagina"])

    for assunto, item in assuntos.items():
        print(
            f"  {assunto:32s} {item['paginas']:3d} págs | "
            f"multimodais: {item['multimodais'] or '-'}"
        )
        total_api += len(item["multimodais"])

    ignoradas = [l["pagina"] for l in linhas if l["metodo"] == "ignorada"]
    print(f"  (páginas ignoradas: {ignoradas or '-'})")

print("\n" + "=" * 80)
print(f"Chamadas estimadas ao modelo visual: {total_api}")
print("=" * 80)
