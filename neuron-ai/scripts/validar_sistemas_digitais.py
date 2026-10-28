"""Aceitação com banco local: catálogo, fontes, prática e correção por assunto."""
import json
import uuid
from app.rag.sistemas_digitais_corpus import RAIZ, DISCIPLINA, carregar_validado
from app.rag.vector_store import VectorStore
from app.practice.material_index import catalogo
from app.practice.repository import QuestionRepository
from app.practice.service import PracticeService


def validar(store=None):
    store=store or VectorStore()
    corpus=carregar_validado()
    materiais,assuntos=catalogo(store,DISCIPLINA)
    assert len(materiais)==12 and len(assuntos)==12
    assert all(m['tipo']=='SLIDE_AULA' and not m['disponivel_para_pratica'] for m in materiais)
    ids=[m['id'] for m in materiais]
    repo=QuestionRepository(store)
    service=PracticeService(repository=repo)
    resumo={};amostra=[]
    for slug,a in assuntos.items():
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=a['disciplina_id'],
                 assunto_id=a['id'],material_ids=ids,origem='MISTO',modo='GERADAS_IA',quantidade=10,
                 excluir_fingerprints=[])
        qs=service.montar_questoes(req)['questoes']
        assert qs and all('gabarito' not in q and 'calculos' not in q for q in qs)
        for q in qs:
            assert all(f['arquivo'] in {m['titulo']+'.pdf' for m in materiais}
                       and f['pagina']>0 for f in q['fontes'])
            segredo=service.sessoes[req['sessao_id']]['questoes'][q['id']]
            correcao=service.corrigir(dict(sessao_id=req['sessao_id'],usuario_id=1,questao_id=q['id'],
                alternativa=segredo['gabarito'],material_ids=ids))
            assert correcao['correto'] and len(correcao['calculos'])>=3
        amostra.extend(dict(assunto=slug,**q) for q in service.sessoes[req['sessao_id']]['questoes'].values())
        resumo[slug]=len(qs)
        req.update(sessao_id=str(uuid.uuid4()),modo='CADASTRADAS')
        assert service.montar_questoes(req)=={'questoes':[]}
    with store._conectar() as c:
        total=c.execute('SELECT count(*) FROM chunk_documento WHERE disciplina=%s AND material_id=ANY(%s)',[DISCIPLINA,ids]).fetchone()[0]
    assert total==corpus['total_chunks']
    relatorio=dict(aprovado=True,materiais=len(materiais),assuntos=len(assuntos),chunks=total,
                   questoes_por_assunto=resumo,questoes_verificadas=sum(resumo.values()),
                   lista_e_prova_cadastradas=False)
    (RAIZ/'saidas_testes/sistemas_digitais_validacao.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
    (RAIZ/'saidas_testes/sistemas_digitais_amostra_resolvida.json').write_text(json.dumps(amostra,ensure_ascii=False,indent=2),encoding='utf-8')
    return relatorio


if __name__=='__main__':
    from scripts.servicos_local import ambiente
    ambiente()
    print(json.dumps(validar(),ensure_ascii=True,indent=2))
