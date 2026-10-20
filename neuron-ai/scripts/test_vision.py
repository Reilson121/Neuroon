import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

with open("pagina_18.png", "rb") as imagem:
    imagem_base64 = base64.b64encode(imagem.read()).decode("utf-8")

response = client.chat.completions.create(
    model=os.getenv("OPENROUTER_VISION_MODEL"),
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
Analise esta página de material acadêmico.

Extraia:
1. título;
2. enunciado;
3. todas as expressões matemáticas;
4. informações relevantes do gráfico;
5. exercícios apresentados.

Não resolva os exercícios.
Preserve a notação matemática o máximo possível.
"""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{imagem_base64}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)