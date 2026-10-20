from app.rag.pptx_processor import PPTXProcessor


CAMINHO = (
    "materiais_academicos/"
    "periodo_04/"
    "teoria_dos_grafos/"
    "aula_02_conceitos_basicos/"
    "Aula 02 - TG - Conceitos Básicos.pptx"
)


processor = PPTXProcessor()

apresentacao = processor.carregar(CAMINHO)

print(f"Total de slides: {len(apresentacao.slides)}")
print()


for numero, slide in enumerate(
    apresentacao.slides,
    start=1
):

    analise = processor.analisar_slide(slide)

    print(
        f"Slide {numero:2} | "
        f"texto={analise['caracteres']:4} | "
        f"imagens={analise['imagens']:2} | "
        f"graficos={analise['graficos']:2} | "
        f"outros={analise['outros_elementos']:2}"
    )