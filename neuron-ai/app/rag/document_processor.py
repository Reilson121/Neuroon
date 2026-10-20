import base64
import os
from pathlib import Path

import pymupdf
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class DocumentProcessor:
    """
    Processador de documentos PDF do NEURON.

    Responsabilidades:
    - extrair texto convencional de páginas;
    - analisar a estrutura visual da página;
    - decidir automaticamente entre extração textual e multimodal;
    - enviar páginas visuais ao modelo de visão;
    - preservar metadados importantes para o futuro RAG.
    """

    def __init__(self):
        self.vision_model = os.getenv(
            "OPENROUTER_VISION_MODEL"
        )

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.client = None

    # =========================================================
    # CLIENTE OPENROUTER
    # =========================================================

    def obter_cliente(self):
        """
        Cria o cliente OpenRouter somente quando
        uma análise multimodal realmente for necessária.

        Isso permite utilizar o detector sem fazer
        nenhuma chamada à API.
        """

        if self.client is None:

            if not self.api_key:
                raise ValueError(
                    "OPENROUTER_API_KEY não encontrada no .env"
                )

            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )

        return self.client

    # =========================================================
    # EXTRAÇÃO TEXTUAL
    # =========================================================

    def extrair_texto_pagina(self, pagina):
        """
        Extrai o texto convencional disponível
        internamente na página do PDF.
        """

        texto = pagina.get_text("text")

        if not texto:
            return ""

        return texto.strip()

    # =========================================================
    # DETECTOR MULTIMODAL
    # =========================================================

    def precisa_multimodal(self, pagina, texto):
        """
        Decide se uma página precisa ser analisada
        pelo modelo multimodal.

        A decisão prioriza a quantidade de texto
        realmente recuperada.

        A simples existência de imagens não é usada
        como critério principal, pois PDFs exportados
        de apresentações podem conter imagens
        decorativas em todas as páginas.
        """

        texto_limpo = texto.strip()

        quantidade_texto = len(
            texto_limpo
        )

        quantidade_desenhos = len(
            pagina.get_drawings()
        )

        motivos = []

        # -----------------------------------------------------
        # CASO 1
        # Nenhum texto recuperado.
        # -----------------------------------------------------

        if quantidade_texto == 0:

            motivos.append(
                "sem_texto_extraivel"
            )

        # -----------------------------------------------------
        # CASO 2
        # Existe texto, mas é muito pouco.
        # -----------------------------------------------------

        elif quantidade_texto < 60:

            motivos.append(
                "texto_muito_curto"
            )

        # -----------------------------------------------------
        # CASO 3
        # Pouco texto + muitos elementos vetoriais.
        #
        # Pode representar:
        # - fluxogramas;
        # - grafos;
        # - mapas;
        # - wireframes;
        # - diagramas.
        # -----------------------------------------------------

        elif (
            quantidade_texto < 140
            and quantidade_desenhos >= 40
        ):

            motivos.append(
                "pouco_texto_com_muitos_elementos_visuais"
            )

        precisa = (
            len(motivos) > 0
        )

        return {
            "precisa_multimodal": precisa,
            "motivos": motivos,
            "caracteres": quantidade_texto,
            "desenhos": quantidade_desenhos,
        }

    # =========================================================
    # ANÁLISE VISUAL
    # =========================================================

    def analisar_pagina_visual(self, pagina):
        """
        Renderiza a página inteira como imagem PNG
        e envia ao modelo multimodal.

        O objetivo é transformar conteúdo visual
        acadêmico em texto útil para o RAG.
        """

        if not self.vision_model:
            raise ValueError(
                "OPENROUTER_VISION_MODEL "
                "não encontrado no .env"
            )

        client = self.obter_cliente()

        # Renderiza em resolução maior para melhorar
        # leitura de textos, fórmulas e diagramas.
        pix = pagina.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            alpha=False
        )

        imagem_bytes = pix.tobytes(
            "png"
        )

        imagem_base64 = base64.b64encode(
            imagem_bytes
        ).decode(
            "utf-8"
        )

        prompt = """
Você está processando material acadêmico para a base de
conhecimento de um sistema RAG chamado NEURON.

Sua tarefa é transformar esta página em texto acadêmico
fiel, claro e útil para recuperação semântica.

Extraia somente informações presentes na página.

Inclua, quando existirem:

- título e subtítulos;
- conceitos;
- definições;
- explicações;
- listas;
- exemplos;
- exercícios e enunciados;
- fórmulas e expressões matemáticas;
- tabelas;
- etapas de processos;
- relações entre elementos de diagramas;
- informações de gráficos;
- grafos;
- fluxogramas;
- mapas de navegação;
- wireframes;
- outros elementos visuais que carreguem
  informação acadêmica relevante.

Quando houver um diagrama, fluxograma, mapa,
wireframe ou outra representação visual importante,
converta sua estrutura e suas relações para texto.

Exemplo:

Página Inicial
→ Cursos
   → Detalhes do curso
   → Conteúdos
→ Perfil
   → Dados pessoais
   → Configurações

IMPORTANTE:

Ignore elementos puramente decorativos, como:

- plantas;
- objetos de escritório;
- ilustrações sem conteúdo acadêmico;
- cores;
- fundos;
- enfeites;
- ícones meramente decorativos.

Só descreva um ícone quando ele tiver significado
necessário para compreender o conteúdo.

Não resolva exercícios.

Não acrescente conhecimento externo.

Não complete informações que não estejam visíveis.

Não deduza conceitos que a página não apresenta.

Não invente nomes, títulos, relações, exemplos,
numeração de slides ou informações ausentes.

Preserve os termos usados pelo próprio material.

Preserve fórmulas e notação matemática o máximo possível.

Evite repetir a mesma informação.

Retorne somente o conteúdo acadêmico útil da página,
em texto estruturado e objetivo.
"""

        resposta = client.chat.completions.create(
            model=self.vision_model,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:image/png;base64,"
                                    + imagem_base64
                                )
                            }
                        }
                    ]
                }
            ]
        )

        conteudo = (
            resposta
            .choices[0]
            .message
            .content
        )

        if not conteudo:
            return ""

        return conteudo.strip()

    # =========================================================
    # DIAGNÓSTICO DE PDF
    # =========================================================

    def diagnosticar_pdf(self, caminho_pdf):
        """
        Analisa um PDF inteiro sem chamar
        o modelo multimodal.

        Serve para descobrir quais páginas
        seriam textuais ou multimodais.

        NÃO consome API.
        """

        caminho = Path(
            caminho_pdf
        )

        if not caminho.exists():
            raise FileNotFoundError(
                f"PDF não encontrado: {caminho}"
            )

        documento = pymupdf.open(
            caminho
        )

        resultados = []

        try:

            for indice, pagina in enumerate(
                documento
            ):

                numero_pagina = (
                    indice + 1
                )

                texto = (
                    self.extrair_texto_pagina(
                        pagina
                    )
                )

                analise = (
                    self.precisa_multimodal(
                        pagina,
                        texto
                    )
                )

                resultados.append(
                    {
                        "pagina": numero_pagina,
                        **analise
                    }
                )

        finally:

            documento.close()

        return resultados

    # =========================================================
    # PROCESSAMENTO DO PDF
    # =========================================================

    def processar_pdf(
        self,
        caminho_pdf,
        periodo,
        disciplina,
        assunto=None,
        aula=None,
        paginas_multimodais=None,
        paginas_textuais=None,
        usar_deteccao_automatica=True
    ):
        """
        Processa um PDF página por página.

        Por padrão, decide automaticamente entre:
        - extração textual;
        - extração multimodal.

        Também permite forçar manualmente páginas
        específicas quando necessário.
        """

        caminho = Path(
            caminho_pdf
        )

        if not caminho.exists():
            raise FileNotFoundError(
                f"PDF não encontrado: {caminho}"
            )

        paginas_multimodais = set(
            paginas_multimodais or []
        )

        paginas_textuais = set(
            paginas_textuais or []
        )

        # -----------------------------------------------------
        # Verifica conflito.
        # -----------------------------------------------------

        conflito = (
            paginas_multimodais
            & paginas_textuais
        )

        if conflito:
            raise ValueError(
                "As seguintes páginas foram "
                "definidas ao mesmo tempo como "
                "textuais e multimodais: "
                f"{sorted(conflito)}"
            )

        documento = pymupdf.open(
            caminho
        )

        resultados = []

        try:

            for indice, pagina in enumerate(
                documento
            ):

                numero_pagina = (
                    indice + 1
                )

                # -------------------------------------------------
                # 1. Tenta extrair texto convencional.
                # -------------------------------------------------

                texto_extraido = (
                    self.extrair_texto_pagina(
                        pagina
                    )
                )

                # -------------------------------------------------
                # 2. Analisa a página.
                #
                # Nenhuma API é chamada nesta etapa.
                # -------------------------------------------------

                analise = (
                    self.precisa_multimodal(
                        pagina,
                        texto_extraido
                    )
                )

                motivos = list(
                    analise["motivos"]
                )

                # -------------------------------------------------
                # 3. Decide o método de extração.
                # -------------------------------------------------

                if (
                    numero_pagina
                    in paginas_multimodais
                ):

                    usar_multimodal = True

                    motivos.append(
                        "multimodal_forcado_manualmente"
                    )

                elif (
                    numero_pagina
                    in paginas_textuais
                ):

                    usar_multimodal = False

                    motivos = [
                        "textual_forcado_manualmente"
                    ]

                elif usar_deteccao_automatica:

                    usar_multimodal = (
                        analise[
                            "precisa_multimodal"
                        ]
                    )

                else:

                    usar_multimodal = False

                    motivos = [
                        "deteccao_automatica_desativada"
                    ]

                # -------------------------------------------------
                # 4. Executa a extração.
                # -------------------------------------------------

                if usar_multimodal:

                    conteudo = (
                        self.analisar_pagina_visual(
                            pagina
                        )
                    )

                    tipo_extracao = (
                        "multimodal"
                    )

                else:

                    conteudo = (
                        texto_extraido
                    )

                    tipo_extracao = (
                        "textual"
                    )

                # -------------------------------------------------
                # 5. Metadados.
                # -------------------------------------------------

                metadata = {
                    "periodo": periodo,
                    "disciplina": disciplina,
                    "assunto": assunto,
                    "aula": aula,
                    "arquivo": caminho.name,
                    "pagina": numero_pagina,
                    "tipo_arquivo": "pdf",
                    "tipo_extracao": tipo_extracao,
                    "motivos_deteccao": motivos,
                    "caracteres_texto_original": (
                        analise["caracteres"]
                    ),
                    "elementos_desenhados": (
                        analise["desenhos"]
                    ),
                }

                resultados.append(
                    {
                        "conteudo": conteudo,
                        "metadata": metadata
                    }
                )

        finally:

            documento.close()

        return resultados