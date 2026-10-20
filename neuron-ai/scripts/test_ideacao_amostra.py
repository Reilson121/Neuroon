import json
from pathlib import Path

import pymupdf

from app.rag.document_processor import DocumentProcessor


PASTA_DISCIPLINA = Path(
    "materiais_academicos/"
    "periodo_03/"
    "projeto_de_ideacao_de_software"
)

PASTA_SAIDA = Path(
    "saidas_testes"
)

PASTA_SAIDA.mkdir(
    exist_ok=True
)


# ---------------------------------------------------------
# Páginas escolhidas para o teste controlado
# ---------------------------------------------------------

AMOSTRAS = {
    "aula_01_introducao": [
        1,
        5,
        20,
    ],

    "aula_02_lean_canvas": [
        1,
        8,
        20,
    ],

    "aula_03_historias_de_usuario": [
        2,
        3,
        5,
    ],

    "aula_04_mapa_de_navegacao_e_wireframe": [
        1,
        7,
        20,
    ],

    "aula_05_matriz_csd": [
        1,
        5,
        10,
    ],
}


processor = DocumentProcessor()

resultados = []


print("=" * 80)
print("TESTE CONTROLADO - PROJETO DE IDEACAO DE SOFTWARE")
print("=" * 80)


for nome_pasta, paginas in AMOSTRAS.items():

    pasta_aula = (
        PASTA_DISCIPLINA
        / nome_pasta
    )

    arquivos_pdf = list(
        pasta_aula.glob("*.pdf")
    )

    if not arquivos_pdf:

        print(
            f"\nERRO: nenhum PDF encontrado em:"
        )

        print(
            pasta_aula
        )

        continue


    caminho_pdf = arquivos_pdf[0]

    print("\n" + "=" * 80)

    print(
        f"ARQUIVO: {caminho_pdf.name}"
    )

    print(
        f"PÁGINAS TESTADAS: {paginas}"
    )

    documento = pymupdf.open(
        caminho_pdf
    )


    try:

        for numero_pagina in paginas:

            print("\n" + "-" * 80)

            print(
                f"Página {numero_pagina}"
            )

            if (
                numero_pagina < 1
                or numero_pagina > len(documento)
            ):

                print(
                    "Página inválida."
                )

                continue


            pagina = documento[
                numero_pagina - 1
            ]


            # -------------------------------------------------
            # 1. Tentativa de extração textual
            # -------------------------------------------------

            texto_extraido = (
                processor.extrair_texto_pagina(
                    pagina
                )
            )


            # -------------------------------------------------
            # 2. Detector
            # -------------------------------------------------

            analise = (
                processor.precisa_multimodal(
                    pagina,
                    texto_extraido
                )
            )


            print(
                f"Caracteres extraídos: "
                f"{analise['caracteres']}"
            )

            print(
                f"Desenhos detectados: "
                f"{analise['desenhos']}"
            )

            print(
                f"Precisa multimodal: "
                f"{analise['precisa_multimodal']}"
            )

            print(
                f"Motivos: "
                f"{analise['motivos']}"
            )


            # -------------------------------------------------
            # 3. Escolha automática do método
            # -------------------------------------------------

            if analise[
                "precisa_multimodal"
            ]:

                print(
                    "Extração: MULTIMODAL"
                )

                print(
                    "Enviando página ao modelo visual..."
                )

                conteudo = (
                    processor.analisar_pagina_visual(
                        pagina
                    )
                )

                tipo_extracao = (
                    "multimodal"
                )

            else:

                print(
                    "Extração: TEXTUAL"
                )

                conteudo = (
                    texto_extraido
                )

                tipo_extracao = (
                    "textual"
                )


            # -------------------------------------------------
            # 4. Resultado
            # -------------------------------------------------

            resultado = {
                "arquivo": caminho_pdf.name,
                "pasta_aula": nome_pasta,
                "pagina": numero_pagina,
                "tipo_extracao": tipo_extracao,
                "caracteres_texto_original": (
                    analise["caracteres"]
                ),
                "desenhos": (
                    analise["desenhos"]
                ),
                "motivos": (
                    analise["motivos"]
                ),
                "conteudo": conteudo,
            }

            resultados.append(
                resultado
            )


            print("\nCONTEÚDO EXTRAÍDO:")
            print("-" * 80)

            if conteudo:

                # Mostra apenas uma parte no terminal
                # para não gerar uma saída gigantesca.

                print(
                    conteudo[:1500]
                )

                if len(conteudo) > 1500:

                    print(
                        "\n[conteúdo continua no arquivo JSON]"
                    )

            else:

                print(
                    "[nenhum conteúdo extraído]"
                )


    finally:

        documento.close()


# ---------------------------------------------------------
# 5. Salvar resultado completo
# ---------------------------------------------------------

arquivo_saida = (
    PASTA_SAIDA
    / "ideacao_amostra_resultado.json"
)


with open(
    arquivo_saida,
    "w",
    encoding="utf-8"
) as arquivo:

    json.dump(
        resultados,
        arquivo,
        ensure_ascii=False,
        indent=4
    )


# ---------------------------------------------------------
# 6. Resumo
# ---------------------------------------------------------

total = len(
    resultados
)

textuais = sum(
    1
    for resultado in resultados
    if resultado["tipo_extracao"]
    == "textual"
)

multimodais = sum(
    1
    for resultado in resultados
    if resultado["tipo_extracao"]
    == "multimodal"
)


print("\n" + "=" * 80)

print("RESUMO DO TESTE")

print("=" * 80)

print(
    f"Páginas processadas: {total}"
)

print(
    f"Textuais: {textuais}"
)

print(
    f"Multimodais: {multimodais}"
)

print(
    f"\nResultado completo salvo em:"
)

print(
    arquivo_saida
)

print("=" * 80)