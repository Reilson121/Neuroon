"""
NEURON - Demonstração do fluxo RAG completo (Aula 03), EM MEMÓRIA.

Fluxo:
    pergunta -> embedding -> Top-K nos chunks -> DeepSeek -> resposta + fontes

Ainda NÃO usa PostgreSQL/pgvector: os chunks vêm do JSON gerado pela
pipeline (saidas_testes/aula_03_pipeline_completa.json).

Como executar (na pasta neuron-ai, com o .venv ativo):

    python -m scripts.test_rag_demo_aula03
    python -m scripts.test_rag_demo_aula03 "Por que histórias de usuário são importantes?"
    python -m scripts.test_rag_demo_aula03 "Qual é a capital da França?"

A última pergunta serve para mostrar o comportamento de
"ausência de evidência" (o sistema não deve inventar resposta).
"""

import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

from app.config.settings import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.rag.embedding_processor import EmbeddingProcessor


# Garante acentos corretos no PowerShell.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# =========================================================
# CONFIGURAÇÃO
# =========================================================

ARQUIVO_CHUNKS = Path(
    "saidas_testes/aula_03_pipeline_completa.json"
)

PERGUNTA_PADRAO = (
    "Qual é a estrutura básica de uma história de usuário?"
)

TOP_K = 3

# Valor INICIAL (palpite), ainda não calibrado.
# Se a melhor similaridade ficar abaixo dele, o sistema
# nem chama o LLM e responde com o fallback.
# Ajuste olhando as similaridades impressas nos testes.
SIMILARIDADE_MINIMA = 0.25

MENSAGEM_FALLBACK = (
    "Não encontrei informações suficientes nos materiais "
    "da disciplina para responder a essa pergunta."
)

PROMPT_SISTEMA = """\
Você é o Monitor Virtual do NEURON, um assistente para estudantes \
de Ciência da Computação.

Responda à pergunta do estudante usando SOMENTE os trechos de \
material fornecidos no contexto.

Regras:
- Não use conhecimento externo e não invente informações.
- Se os trechos não contiverem informação suficiente para \
responder, responda exatamente: \
"Não encontrei informações suficientes nos materiais da \
disciplina para responder a essa pergunta."
- Responda em português do Brasil, de forma clara e didática.
- Não escreva a lista de fontes; ela será exibida pelo sistema.
"""


# =========================================================
# FUNÇÕES
# =========================================================

def carregar_chunks(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de chunks não encontrado: {caminho}\n"
            "Execute antes: python -m scripts.test_pipeline_aula03"
        )

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados["chunks"]


def buscar_top_k(embedding_pergunta, chunks_com_embedding, k):
    """
    Como os embeddings são normalizados, o produto escalar
    equivale à similaridade de cosseno.
    """

    resultados = []

    for chunk in chunks_com_embedding:
        similaridade = float(
            np.dot(
                embedding_pergunta,
                np.array(chunk["embedding"])
            )
        )

        resultados.append(
            {
                "similaridade": similaridade,
                "chunk": chunk,
            }
        )

    resultados.sort(
        key=lambda item: item["similaridade"],
        reverse=True
    )

    return resultados[:k]


def montar_contexto(resultados):
    """
    Junta os trechos recuperados, identificando a origem
    de cada um (aula e página).
    """

    blocos = []

    for item in resultados:
        metadata = item["chunk"]["metadata"]

        cabecalho = (
            f"[Aula {metadata.get('aula')} - "
            f"{metadata.get('assunto')} - "
            f"página {metadata.get('pagina')}]"
        )

        blocos.append(
            f"{cabecalho}\n{item['chunk']['conteudo']}"
        )

    return "\n\n---\n\n".join(blocos)


def gerar_resposta(pergunta, contexto):
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY não encontrada no .env"
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    resposta = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": PROMPT_SISTEMA
            },
            {
                "role": "user",
                "content": (
                    f"CONTEXTO:\n{contexto}\n\n"
                    f"PERGUNTA DO ESTUDANTE:\n{pergunta}"
                )
            },
        ],
    )

    conteudo = resposta.choices[0].message.content

    return (conteudo or "").strip()


def imprimir_fontes(resultados):
    """
    As fontes vêm dos METADADOS dos chunks recuperados,
    e não do texto gerado pelo LLM. Assim elas são sempre
    reais e rastreáveis.
    """

    print("\nFONTES CONSULTADAS:")

    for posicao, item in enumerate(resultados, start=1):
        metadata = item["chunk"]["metadata"]

        print(
            f"  {posicao}. Aula {metadata.get('aula')} - "
            f"{metadata.get('assunto')} | "
            f"página {metadata.get('pagina')} | "
            f"extração: {metadata.get('tipo_extracao')} | "
            f"similaridade: {item['similaridade']:.4f} | "
            f"chunk_id: {item['chunk']['chunk_id']}"
        )


# =========================================================
# EXECUÇÃO
# =========================================================

def main():
    pergunta = (
        " ".join(sys.argv[1:]).strip()
        or PERGUNTA_PADRAO
    )

    print("=" * 80)
    print("NEURON - DEMO DO MONITOR VIRTUAL (Aula 03, em memória)")
    print("=" * 80)

    print(f"\nPergunta: {pergunta}")

    # 1. Chunks
    chunks = carregar_chunks(ARQUIVO_CHUNKS)
    print(f"\nChunks carregados: {len(chunks)}")

    # 2. Embeddings
    processor = EmbeddingProcessor()
    chunks_com_embedding = processor.processar_chunks(chunks)
    print(f"Embeddings gerados: {len(chunks_com_embedding)}")

    # 3. Busca Top-K
    embedding_pergunta = np.array(
        processor.gerar_embedding(pergunta)
    )

    resultados = buscar_top_k(
        embedding_pergunta,
        chunks_com_embedding,
        TOP_K
    )

    melhor = resultados[0]["similaridade"]

    print(
        f"\nMelhor similaridade: {melhor:.4f} "
        f"(mínimo configurado: {SIMILARIDADE_MINIMA})"
    )

    # 4. Ausência de evidência: não chama o LLM.
    if melhor < SIMILARIDADE_MINIMA:
        print("\n" + "=" * 80)
        print("RESPOSTA")
        print("=" * 80)
        print(f"\n{MENSAGEM_FALLBACK}")
        print("\n(Fallback acionado antes de chamar o LLM.)")
        imprimir_fontes(resultados)
        return

    # 5. Geração da resposta
    contexto = montar_contexto(resultados)

    print("\nChamando o modelo (OpenRouter)...")

    resposta = gerar_resposta(pergunta, contexto)

    print("\n" + "=" * 80)
    print("RESPOSTA")
    print("=" * 80)
    print(f"\n{resposta}")

    # Se o LLM declarou falta de informação, as fontes
    # não sustentam a resposta e não devem ser apresentadas
    # como se sustentassem.
    if "Não encontrei informações suficientes" in resposta:
        print("\n(O modelo indicou que os trechos não bastam.)")
        return

    imprimir_fontes(resultados)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()