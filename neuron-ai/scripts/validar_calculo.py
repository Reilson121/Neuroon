"""Verificação integrada usando o banco local, sem criar dados de estudante."""
import json
import uuid
from app.rag.calculo_corpus import DISCIPLINA,RAIZ
from app.practice.material_index import catalogo,permitido
from app.practice.calculo_engine import TOPICOS
from app.practice.service import PracticeService


def validar(monitor=False):
    from app.rag.vector_store import VectorStore
    store=VectorStore();materiais,assuntos=catalogo(store,DISCIPLINA)
    assert len(materiais)==5 and len(assuntos)==9
    service=PracticeService();amostras=[]
    for topico,(slug,unidade,_,tipos) in TOPICOS.items():
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=materiais[0]['disciplina_id'],
            assunto_id=assuntos[slug]['id'],material_ids=[m['id'] for m in materiais if permitido(m)],
            origem='MISTO',modo='GERADAS_IA',quantidade=1,unidade_calculo=unidade,topico_calculo=topico,tipo_funcao=tipos[0])
        qs=service.montar_questoes(req)['questoes'];assert len(qs)==1,topico
        q=qs[0];assert not {'gabarito','calculos','spec','resolucao'}&q.keys()
        segredo=service.sessoes[req['sessao_id']]['questoes'][q['id']]
        c=service.corrigir(dict(sessao_id=req['sessao_id'],usuario_id=1,questao_id=q['id'],alternativa=segredo['gabarito'],material_ids=req['material_ids']))
        assert c['correto'] and c['calculos']
        amostras.append(dict(topico=topico,unidade=unidade,fontes=q['fontes'],passos=len(c['calculos'])))
    relatorio=dict(periodo=2,topicos_conferidos=len(amostras),amostras=amostras)
    destino=RAIZ/'saidas_testes/calculo_validacao.json'
    if monitor:
        from app.rag.monitor_virtual import MonitorVirtual
        import torch
        torch.set_num_threads(1)
        tutor=MonitorVirtual();respostas=[]
        for pergunta,slug in [('Explique a regra da cadeia e indique a tabela de apoio.','regras_derivacao'),
                ('Como se calcula a função inversa?','funcoes_inversas'),
                ('O que a questão 8 da prova informa sobre continuidade em x = 1?','continuidade')]:
            r=tutor.responder(pergunta,DISCIPLINA,slug)
            respostas.append(dict(pergunta=pergunta,**r))
            relatorio['monitor']=respostas
            destino.write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(dict(assunto=slug,fallback=r['fallback'],fontes=len(r['fontes']))),flush=True)
        relatorio['monitor']=respostas
        assert all(not r['fallback'] and r['fontes'] for r in respostas),[(r['pergunta'],r.get('motivo')) for r in respostas if r['fallback']]
    (RAIZ/'saidas_testes/calculo_validacao.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(topicos_conferidos=len(amostras),monitor_conferido=monitor)),flush=True)


if __name__=='__main__':
    import argparse
    from scripts.servicos_local import ambiente
    ambiente();p=argparse.ArgumentParser();p.add_argument('--monitor',action='store_true');validar(p.parse_args().monitor)
