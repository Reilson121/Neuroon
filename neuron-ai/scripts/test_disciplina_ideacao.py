from pathlib import Path


PASTA_DISCIPLINA = Path(
    "materiais_academicos/"
    "periodo_03/"
    "projeto_de_ideacao_de_software"
)


print("=" * 60)
print("TESTE DA DISCIPLINA - PROJETO DE IDEACAO DE SOFTWARE")
print("=" * 60)

if not PASTA_DISCIPLINA.exists():
    print("\nERRO: pasta não encontrada:")
    print(PASTA_DISCIPLINA)
    raise SystemExit()


arquivos = sorted(
    PASTA_DISCIPLINA.rglob("*.pdf")
)


print("\nPasta encontrada:")
print(PASTA_DISCIPLINA)

print(f"\nTotal de PDFs encontrados: {len(arquivos)}")


for numero, arquivo in enumerate(arquivos, start=1):

    caminho_relativo = arquivo.relative_to(PASTA_DISCIPLINA)

    print(f"\n{numero}. {caminho_relativo}")


print("\n" + "=" * 60)

if len(arquivos) == 5:
    print("OK: os 5 materiais foram encontrados.")
else:
    print(
        f"ATENCAO: esperavamos 5 PDFs, "
        f"mas encontramos {len(arquivos)}."
    )

print("=" * 60)