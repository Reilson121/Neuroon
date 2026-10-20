from app.rag.document_processor import DocumentProcessor


CAMINHO_PDF = (
    "materiais_academicos/"
    "periodo_02/"
    "calculo_para_computacao_1/"
    "limites/"
    "Aulas_Limites_2020_1.pdf"
)


processor = DocumentProcessor()

documentos = processor.processar_pdf(
    caminho_pdf=CAMINHO_PDF,
    periodo=2,
    disciplina="calculo_para_computacao_1",
    assunto="limites",
    paginas_multimodais=[3, 17, 18]
)


for numero in [2, 3, 17, 18]:
    documento = documentos[numero - 1]

    print("\n" + "=" * 70)
    print(documento["metadata"])
    print("=" * 70)
    print(documento["conteudo"][:3000])