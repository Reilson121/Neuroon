"""Confere catálogo, busca e simulados de integrais no banco configurado."""
import json
import uuid
from dotenv import load_dotenv
from app.rag.integral_corpus import RAIZ,DISCIPLINA

def validar():
    load_dotenv(RAIZ/'.env');load_dotenv(RAIZ.parent/'.env')
    from app.rag.vector_store import VectorStore
    from app.practice.material_index import catalogo
    from app.practice.repository import QuestionRepository
    from app.practice.service import PracticeService
    from app.practice.integral_engine import TOPICOS
    store=VectorStore();materiais,assuntos=catalogo(store,DISCIPLINA)
    if len(materiais)!=4 or len(assuntos)!=8:raise ValueError('Catálogo de Cálculo II incompleto.')
    repo=QuestionRepository(store);resultados=[]
    for unidade in [1,2,0]:
        slugs={v[0] for v in TOPICOS.values() if v[1]>0 and (not unidade or v[1]==unidade)}
        ids=[assuntos[slug]['id'] for slug in slugs]
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=materiais[0]['disciplina_id'],assunto_id=None,
            assunto_ids=ids,material_ids=[m['id'] for m in materiais],origem='MISTO',modo='GERADAS_IA',quantidade=10,unidade_calculo=unidade)
        svc=PracticeService(repository=repo);publicas=svc.montar_questoes(req)['questoes']
        if len(publicas)!=10 or any('gabarito' in q or 'calculos' in q for q in publicas):raise ValueError('Simulado incompleto ou gabarito exposto.')
        qs=svc.sessoes[req['sessao_id']]['questoes'].values()
        if {TOPICOS[q['spec']['topico']][0] for q in qs}!=slugs:raise ValueError('Cobertura incompleta.')
        resultados.append(dict(unidade=unidade,questoes=len(publicas),assuntos=len(ids)))
    resultado=dict(disciplina=DISCIPLINA,periodo=3,materiais=len(materiais),assuntos=len(assuntos),simulados=resultados)
    (RAIZ/'saidas_testes/calculo2_validacao.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf-8')
    return resultado

if __name__=='__main__':print(json.dumps(validar(),ensure_ascii=False,indent=2))
