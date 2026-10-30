"""Usa o índice e as permissões compartilhados; mantém ED Avançada isolada."""
import json
from app.practice.material_index import catalogo,indexar,permitido
from app.rag.ed_basica_corpus import DISCIPLINA,carregar_validado,preparar_material,RAIZ


def integrar(store=None):
    from app.rag.vector_store import VectorStore
    from app.rag.embedding_processor import EmbeddingProcessor
    store=store or VectorStore();dados=carregar_validado()
    materiais,assuntos=catalogo(store,DISCIPLINA)
    if {m['referencia_externa'] for m in materiais}!={'local:'+a['pdf'] for a in dados['arquivos']}:
        raise ValueError('Aplique a migration V10 antes de integrar os materiais.')
    for m in materiais:
        if permitido(m):preparar_material(m,assuntos)
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
            raise ValueError('Busca não preservou o assunto e o segundo período: '+slug)
    return dict(periodo=2,disciplina=DISCIPLINA,materiais=resultado,chunks=dados['total_chunks'],buscas_conferidas=len(assuntos))


if __name__=='__main__':
    from scripts.servicos_local import ambiente
    ambiente();resultado=integrar()
    (RAIZ/'saidas_testes/ed_basica_integracao.json').write_text(json.dumps(resultado,indent=2),encoding='utf-8')
    print(json.dumps(resultado,indent=2))
