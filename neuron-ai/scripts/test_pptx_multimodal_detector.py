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

candidatos = []

for numero, slide in enumerate(
    apresentacao.slides,
    start=1
):
    resultado = processor.precisa_multimodal(slide)

    if resultado["precisa_multimodal"]:
        candidatos.append(numero)

        print(
            f"Slide {numero:2} | "
            f"texto={resultado['caracteres']:4} | "
            f"imagens={resultado['imagens']:2} | "
            f"graficos={resultado['graficos']:2} | "
            f"outros={resultado['outros_elementos']:2} | "
            f"motivos={', '.join(resultado['motivos'])}"
        )


print("\n" + "=" * 70)
print("RESULTADO")
print("=" * 70)

print(
    f"Total de slides: "
    f"{len(apresentacao.slides)}"
)

print(
    f"Candidatos multimodais: "
    f"{len(candidatos)}"
)

print(
    f"Slides candidatos: "
    f"{candidatos}"
)