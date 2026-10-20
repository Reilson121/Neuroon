import pymupdf

CAMINHO_PDF = (
    "materiais_academicos/"
    "periodo_02/"
    "calculo_para_computacao_1/"
    "limites/"
    "Aulas_Limites_2020_1.pdf"
)

documento = pymupdf.open(CAMINHO_PDF)

# Página 18 = índice 17
pagina = documento[17]

# Renderiza com boa resolução
pix = pagina.get_pixmap(matrix=pymupdf.Matrix(2, 2))

pix.save("pagina_18.png")

print("Página 18 salva como pagina_18.png")