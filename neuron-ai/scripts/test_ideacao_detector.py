from pathlib import Path

import pymupdf

from app.rag.document_processor import DocumentProcessor


PASTA_DISCIPLINA = Path(
    "materiais_academicos/"
    "periodo_03/"
    "projeto_de_ideacao_de_software"
)


processor = DocumentProcessor()

arquivos = sorted(
    PASTA_DISCIPLINA.rglob("*.pdf")
)


print("=" * 75)
print("DIAGNOSTICO - PROJETO DE IDEACAO DE SOFTWARE")
print("=" * 75)


for arquivo in arquivos:

    print(f"\nARQUIVO: {arquivo.name}")

    documento = pymupdf.open(arquivo)

    total_paginas = len(documento)

    paginas_textuais = []
    paginas_multimodais = []

    for numero_pagina, pagina in enumerate(
        documento,
        start=1
    ):

        texto = processor.extrair_texto_pagina(pagina)

        resultado = processor.precisa_multimodal(
            pagina,
            texto
        )

        if resultado["precisa_multimodal"]:
            paginas_multimodais.append(numero_pagina)

        else:
            paginas_textuais.append(numero_pagina)


    print(f"Total de paginas: {total_paginas}")

    print(
        f"Paginas textuais: "
        f"{len(paginas_textuais)}"
    )

    print(
        f"Paginas multimodais: "
        f"{len(paginas_multimodais)}"
    )

    print(
        f"Candidatas multimodais: "
        f"{paginas_multimodais}"
    )

    documento.close()

    print("-" * 75)


print("\nDIAGNOSTICO CONCLUIDO")