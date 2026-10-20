from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


def carregar_pdf(caminho_pdf: str):
    caminho = Path(caminho_pdf)

    if not caminho.exists():
        raise FileNotFoundError(f"PDF não encontrado: {caminho}")

    loader = PyPDFLoader(str(caminho))
    paginas = loader.load()

    return paginas