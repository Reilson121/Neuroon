"""Integra os doze PDFs; não cadastra lista nem prova inexistentes."""
import json
from app.practice.material_index import catalogo, indexar, permitido
from app.rag.sistemas_digitais_corpus import DISCIPLINA, RAIZ, carregar_validado, preparar_material
from app.rag.vector_store import VectorStore


def integrar(store=None):
    dados=carregar_validado()
    store=store or VectorStore()
    materiais,assuntos=catalogo(store,DISCIPLINA)
    esperados={'local:'+a['pdf'] for a in dados['arquivos']}
    if len(materiais)!=12 or {m['referencia_externa'] for m in materiais}!=esperados:
        raise ValueError('Aplique a migration V7 antes da integração.')
    for m in materiais:
        if permitido(m): preparar_material(m,assuntos)
    # O mesmo modelo atende ao lote todo, evitando recarregá-lo a cada PDF.
    from app.rag.embedding_processor import EmbeddingProcessor
    embedder=EmbeddingProcessor()
    resultado={}
    for m in materiais:
        if permitido(m):
            print('Indexando: '+m['titulo'],flush=True)
            resultado[str(m['id'])]=indexar(m['id'],store,embedder=embedder)
    from app.rag.retriever import Retriever
    retriever=Retriever(embedder=embedder,store=store)
    for slug,a in assuntos.items():
        encontrados=retriever.recuperar(a['nome'],DISCIPLINA,slug)
        if not encontrados or any(q['metadata']['assunto_id']!=a['id'] or
                q['metadata']['disciplina_id']!=a['disciplina_id'] for q in encontrados):
            raise ValueError('Busca do Monitor não preservou o assunto: '+slug)
    from scripts.validar_sistemas_digitais import validar
    validacao=validar(store)
    return dict(materiais=resultado,total_materiais=len(resultado),total_chunks=dados['total_chunks'],
                buscas_por_assunto_conferidas=len(assuntos),pratica=validacao)


if __name__=='__main__':
    resultado=integrar()
    (RAIZ/'saidas_testes/sistemas_digitais_integracao.json').write_text(json.dumps(resultado,indent=2),encoding='utf-8')
    print(json.dumps(resultado,indent=2))
