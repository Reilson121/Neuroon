from app.rag.loader import carregar_pdf


CAMINHO_PDF = (
    "materiais_academicos/"
    "periodo_02/"
    "calculo_para_computacao_1/"
    "limites/"
    "Aulas_Limites_2020_1.pdf"
)


paginas = carregar_pdf(CAMINHO_PDF)

print(f"Total de páginas carregadas: {len(paginas)}")

for pagina in paginas[:3]:
    print("\n" + "=" * 60)

    numero_pagina = pagina.metadata.get("page", 0) + 1

    print(f"PÁGINA {numero_pagina}")
    print("=" * 60)

    print(pagina.page_content[:1500])

    from app.rag.loader import carregar_pdf


CAMINHO_PDF = (
    "materiais_academicos/"
    "periodo_02/"
    "calculo_para_computacao_1/"
    "limites/"
    "Aulas_Limites_2020_1.pdf"
)

paginas = carregar_pdf(CAMINHO_PDF)

print(f"Total de páginas carregadas: {len(paginas)}")

palavras_chave = [
    "exercício",
    "exercícios",
    "atividade",
    "questão"
]

encontradas = 0

for pagina in paginas:
    texto = pagina.page_content.lower()

    if any(palavra in texto for palavra in palavras_chave):
        numero = pagina.metadata.get("page", 0) + 1

        print("\n" + "=" * 70)
        print(f"PÁGINA {numero}")
        print("=" * 70)
        print(pagina.page_content[:2500])

        encontradas += 1

        if encontradas == 3:
            break

if encontradas == 0:
    print("Nenhuma página de exercício encontrada pelas palavras-chave.")