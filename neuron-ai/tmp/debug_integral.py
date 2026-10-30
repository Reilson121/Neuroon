from dotenv import load_dotenv
load_dotenv('.env')
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.rag.integral_search import ordenar_evidencias
from app.practice.material_index import catalogo
from unittest.mock import Mock
v=VectorStore()
with v._conectar() as c:
    rows=c.execute("SELECT assunto,periodo,metadata->>'unidade',metadata->>'assunto_id',count(*) FROM chunk_documento WHERE disciplina='calculo_para_computacao_2' GROUP BY 1,2,3,4").fetchall()
    print(rows)
    emb=c.execute("SELECT embedding FROM chunk_documento WHERE disciplina='calculo_para_computacao_2' LIMIT 1").fetchone()[0]
import json
e=Mock();e.gerar_embedding.return_value=json.loads(emb) if isinstance(emb,str) else list(emb)
r=Retriever(embedder=e,store=v)
for slug,a in catalogo(v,'calculo_para_computacao_2')[1].items():
    if slug=='integrais_duplas_retangulares':
        candidatos=v.buscar_hibridos(e.gerar_embedding.return_value,a['nome'],'calculo_para_computacao_2',assunto=slug,k=50)
        print('CANDIDATOS',len(candidatos),[(z.get('assunto'),z['metadata'].get('assunto'),z['metadata'].get('complementar'),z['metadata'].get('unidade')) for z in candidatos[:2]])
    rs=r.recuperar(a['nome'],'calculo_para_computacao_2',slug)
    print(slug,a['id'],len(rs),[(z['metadata'].get('assunto_id'),z['metadata'].get('periodo'),z['metadata'].get('unidade')) for z in rs])
