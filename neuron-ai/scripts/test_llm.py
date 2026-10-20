from langchain_openrouter import ChatOpenRouter

from app.config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL
)

llm = ChatOpenRouter(
    model=OPENROUTER_MODEL,
    api_key=OPENROUTER_API_KEY,
    temperature=0
)

resposta = llm.invoke(
    "Responda somente: conexão do NEURON com o DeepSeek funcionando."
)

print(resposta.content)