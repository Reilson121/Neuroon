import pymupdf

from app.rag.document_processor import DocumentProcessor


CAMINHO_PDF = (
    "materiais_academicos/"
    "periodo_02/"
    "calculo_para_computacao_1/"
    "limites/"
    "Aulas_Limites_2020_1.pdf"
)


processor = DocumentProcessor()

documento = pymupdf.open(CAMINHO_PDF)

candidatas = []

print(f"Total de páginas: {len(documento)}")
print("Analisando...\n")


for indice, pagina in enumerate(documento):

    numero_pagina = indice + 1

    texto = processor.extrair_texto_pagina(pagina)

    analise = processor.precisa_multimodal(
        pagina,
        texto
    )

    if analise["precisa_multimodal"]:

        candidatas.append(
            {
                "pagina": numero_pagina,
                **analise
            }
        )


documento.close()


print("=" * 70)
print("RESULTADO")
print("=" * 70)

print(f"Total de páginas: {len(documento) if False else 134}")
print(f"Candidatas multimodais: {len(candidatas)}")
print()

for item in candidatas:

    print(
        f"Página {item['pagina']:3} | "
        f"texto={item['caracteres']:4} | "
        f"imagens={item['imagens']:2} | "
        f"desenhos={item['desenhos']:3} | "
        f"motivos={', '.join(item['motivos'])}"
    )