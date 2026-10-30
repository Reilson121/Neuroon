"""Integra somente o corpus de Cálculo, preservando as demais disciplinas."""
import json
import os
from app.practice.material_index import catalogo,indexar,permitido
from app.rag.calculo_corpus import DISCIPLINA,carregar_validado,preparar_material,RAIZ


def integrar(store=None):
    # Evita que bibliotecas de inferência disputem todos os núcleos com o servidor.
    os.environ.setdefault('OMP_NUM_THREADS','1')
    from app.rag.vector_store import VectorStore
    from app.rag.embedding_processor import EmbeddingProcessor
    import torch
    torch.set_num_threads(1)
    store=store or VectorStore();dados=carregar_validado()
    materiais,assuntos=catalogo(store,DISCIPLINA)
    if {m['referencia_externa'] for m in materiais}!={'local:'+a['pdf'] for a in dados['arquivos']}:
        raise ValueError('Aplique a migration V11 antes de integrar os materiais de Cálculo.')
    for m in materiais:
        if permitido(m):preparar_material(m,assuntos)
    print('Carregando embeddings para o corpus conferido de Cálculo.',flush=True)
    embedder=EmbeddingProcessor();resultado={}
    for m in materiais:
        if permitido(m):
            print('Indexando: '+m['titulo'],flush=True)
            resultado[str(m['id'])]=indexar(m['id'],store,embedder=embedder)
    from app.rag.retriever import Retriever
    retriever=Retriever(embedder=embedder,store=store)
    for slug,a in assuntos.items():
        encontrados=retriever.recuperar(a['nome'],DISCIPLINA,slug)
        if not encontrados or any(c['metadata']['disciplina_id']!=a['disciplina_id'] or
                c['metadata']['assunto_id']!=a['id'] or c['metadata']['periodo']!='02' for c in encontrados):
            raise ValueError('Busca fora do assunto ou do segundo período: '+slug)
    return dict(periodo=2,disciplina=DISCIPLINA,materiais=resultado,chunks=dados['total_chunks'],buscas_conferidas=len(assuntos))


if __name__=='__main__':
    from dotenv import load_dotenv
    load_dotenv(RAIZ/'.env');load_dotenv(RAIZ.parent/'.env')
    resultado=integrar()
    # Em produção, a imagem e o volume de materiais são somente leitura.
    # O relatório continua disponível em stdout, sem exigir escrita na imagem.
    relatorio=RAIZ/'saidas_testes/calculo_integracao.json'
    if os.access(relatorio.parent,os.W_OK):
        relatorio.write_text(json.dumps(resultado,indent=2),encoding='utf-8')
    print(json.dumps(resultado,indent=2))
