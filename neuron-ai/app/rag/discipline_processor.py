import json
from pathlib import Path

from app.rag.document_processor import DocumentProcessor
from app.rag.chunk_processor import ChunkProcessor


class DisciplineProcessor:
    """
    Orquestra a ingestão dos materiais acadêmicos.

    Fluxo:

    PDF
        ↓
    DocumentProcessor
        ↓
    páginas processadas
        ↓
    ChunkProcessor
        ↓
    chunks prontos para embeddings
    """

    def __init__(
        self,
        chunk_size=1000,
        chunk_overlap=150
    ):
        self.document_processor = (
            DocumentProcessor()
        )

        self.chunk_processor = (
            ChunkProcessor(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        )

    # =========================================================
    # LOCALIZAR PDF
    # =========================================================

    def localizar_pdf(self, pasta_aula):
        """
        Localiza o PDF existente dentro
        da pasta de uma aula.

        Para o MVP, esperamos exatamente
        um PDF por pasta de aula.
        """

        pasta = Path(
            pasta_aula
        )

        if not pasta.exists():
            raise FileNotFoundError(
                f"Pasta da aula não encontrada: {pasta}"
            )

        arquivos = sorted(
            pasta.glob("*.pdf")
        )

        if len(arquivos) == 0:
            raise FileNotFoundError(
                f"Nenhum PDF encontrado em: {pasta}"
            )

        if len(arquivos) > 1:
            raise ValueError(
                "Mais de um PDF encontrado na pasta "
                f"{pasta}. Para este MVP esperamos "
                "um PDF por pasta de aula."
            )

        return arquivos[0]

    # =========================================================
    # PROCESSAR UMA AULA
    # =========================================================

    def processar_aula(
        self,
        pasta_aula,
        periodo,
        disciplina,
        assunto,
        aula,
        paginas_multimodais=None,
        paginas_textuais=None,
        usar_deteccao_automatica=True
    ):
        """
        Processa uma aula completa.

        Retorna:
        - informações da aula;
        - páginas processadas;
        - chunks gerados;
        - resumo.
        """

        pasta = Path(
            pasta_aula
        )

        caminho_pdf = (
            self.localizar_pdf(
                pasta
            )
        )

        # -----------------------------------------------------
        # 1. PROCESSAMENTO DO DOCUMENTO
        # -----------------------------------------------------

        paginas = (
            self.document_processor.processar_pdf(
                caminho_pdf=caminho_pdf,
                periodo=periodo,
                disciplina=disciplina,
                assunto=assunto,
                aula=aula,
                paginas_multimodais=paginas_multimodais,
                paginas_textuais=paginas_textuais,
                usar_deteccao_automatica=(
                    usar_deteccao_automatica
                )
            )
        )

        # -----------------------------------------------------
        # 2. ENRIQUECER METADADOS
        # -----------------------------------------------------

        for pagina in paginas:

            metadata = pagina[
                "metadata"
            ]

            metadata[
                "pasta_aula"
            ] = pasta.name

        # -----------------------------------------------------
        # 3. CHUNKING
        # -----------------------------------------------------

        chunks = (
            self.chunk_processor
            .processar_resultados(
                paginas
            )
        )

        # -----------------------------------------------------
        # 4. ESTATÍSTICAS
        # -----------------------------------------------------

        paginas_textuais_total = sum(
            1
            for pagina in paginas
            if (
                pagina["metadata"][
                    "tipo_extracao"
                ]
                == "textual"
            )
        )

        paginas_multimodais_total = sum(
            1
            for pagina in paginas
            if (
                pagina["metadata"][
                    "tipo_extracao"
                ]
                == "multimodal"
            )
        )

        resumo = {
            "arquivo": caminho_pdf.name,
            "periodo": periodo,
            "disciplina": disciplina,
            "assunto": assunto,
            "aula": aula,
            "total_paginas": len(
                paginas
            ),
            "paginas_textuais": (
                paginas_textuais_total
            ),
            "paginas_multimodais": (
                paginas_multimodais_total
            ),
            "total_chunks": len(
                chunks
            ),
            "chunk_size": (
                self.chunk_processor.chunk_size
            ),
            "chunk_overlap": (
                self.chunk_processor.chunk_overlap
            ),
        }

        return {
            "resumo": resumo,
            "paginas": paginas,
            "chunks": chunks
        }

    # =========================================================
    # PROCESSAR DISCIPLINA
    # =========================================================

    def processar_disciplina(
        self,
        pasta_disciplina,
        periodo,
        disciplina,
        aulas
    ):
        """
        Processa várias aulas de uma disciplina.

        O parâmetro 'aulas' deve seguir o formato:

        {
            "aula_01_introducao": {
                "aula": "01",
                "assunto": "introducao"
            }
        }

        No momento vamos testar apenas uma aula.
        """

        pasta_base = Path(
            pasta_disciplina
        )

        resultados_aulas = []

        todos_chunks = []

        for nome_pasta, configuracao in aulas.items():

            pasta_aula = (
                pasta_base
                / nome_pasta
            )

            resultado = (
                self.processar_aula(
                    pasta_aula=pasta_aula,
                    periodo=periodo,
                    disciplina=disciplina,
                    assunto=configuracao[
                        "assunto"
                    ],
                    aula=configuracao[
                        "aula"
                    ]
                )
            )

            resultados_aulas.append(
                resultado
            )

            todos_chunks.extend(
                resultado[
                    "chunks"
                ]
            )

        return {
            "periodo": periodo,
            "disciplina": disciplina,
            "total_aulas": len(
                resultados_aulas
            ),
            "total_chunks": len(
                todos_chunks
            ),
            "aulas": resultados_aulas,
            "chunks": todos_chunks
        }

    # =========================================================
    # SALVAR JSON
    # =========================================================

    def salvar_json(
        self,
        dados,
        caminho_saida
    ):
        """
        Salva resultados da ingestão em JSON.
        """

        caminho = Path(
            caminho_saida
        )

        caminho.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            caminho,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )