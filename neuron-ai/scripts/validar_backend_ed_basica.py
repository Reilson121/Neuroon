"""Aceitação HTTP da disciplina básica; remove a conta de teste no finally."""
import json
import secrets
import uuid
from scripts.servicos_local import ambiente,ROOT
from scripts.validar_backend_estatistica import Cliente
from app.rag.vector_store import VectorStore


def main(com_provedor=False):
    ambiente();store=VectorStore();cliente=Cliente();checks=[];amostra=None
    email='validacao-ed-basica-'+uuid.uuid4().hex+'@example.test';senha='Teste!'+secrets.token_urlsafe(24)
    try:
        cliente.chamar('GET','/api/v1/periodos',status=401)
        cliente.chamar('POST','/api/v1/auth/cadastro',dict(nome='Validação temporária ED básica',email=email,senha=senha),status=201)
        cliente.login(email,senha)
        periodos=cliente.chamar('GET','/api/v1/periodos');p=next(p for p in periodos if p['numero']==2)
        ds=cliente.chamar('GET',f"/api/v1/periodos/{p['id']}/disciplinas")
        d=next(d for d in ds if d['nome']=='Estrutura de Dados');did=d['id']
        assert d['periodoId']==p['id'];checks.append('Disciplina básica no segundo período')
        terceiro=next(p for p in periodos if p['numero']==3)
        avancadas=cliente.chamar('GET',f"/api/v1/periodos/{terceiro['id']}/disciplinas")
        assert all(d['nome']!='Estrutura de Dados' for d in avancadas)
        assert any(d['nome']=='Estrutura de Dados Avançada' for d in avancadas)
        checks.append('Disciplina avançada preservada no terceiro período')
        assuntos=cliente.chamar('GET',f'/api/v1/disciplinas/{did}/assuntos')
        materiais=cliente.chamar('GET',f'/api/v1/disciplinas/{did}/materiais')
        assert len(assuntos)==9 and len(materiais)==10
        for m in materiais:
            resposta=cliente.http.get(f"/api/v1/materiais/{m['id']}/arquivo")
            assert resposta.status_code==200 and resposta.content.startswith(b'%PDF')
        checks.append('Nove assuntos e dez PDFs pela API autenticada')
        base=dict(disciplinaId=did,origem='MISTO',modo='GERADAS_IA',quantidade=1,tipoQuestao='TESTE_MESA',nivelContexto='DIRETO')
        for a in assuntos:
            sessao=cliente.chamar('POST','/api/v1/pratica/sessoes',dict(base,assuntoId=a['id']),status=201)
            assert len(sessao['questoes'])==1
            q=sessao['questoes'][0];assert not {'gabarito','spec','calculos','resolucao'}&q.keys()
            correcao=cliente.chamar('POST',f"/api/v1/pratica/sessoes/{sessao['sessaoId']}/respostas",dict(questaoId=q['id'],alternativa='A'))
            assert correcao['calculos'] and 'Pseudocódigo de apoio' in correcao['resolucao'] and 'Teste de mesa resolvido' in correcao['resolucao']
            assert correcao['alternativaCorreta'] in q['alternativas']
        checks.append('Testes de mesa e correções completos nos nove assuntos')
        sessao=cliente.chamar('POST','/api/v1/pratica/sessoes',dict(base,modo='CADASTRADAS',origem='PROVA',quantidade=10),status=201)
        assert len(sessao['questoes'])==4
        for q in sessao['questoes']:
            numero=int(q['fontes'][0]['numeroQuestao']);letra={1:'C',2:'D',3:'E',4:'B'}[numero]
            correcao=cliente.chamar('POST',f"/api/v1/pratica/sessoes/{sessao['sessaoId']}/respostas",dict(questaoId=q['id'],alternativa=letra))
            assert correcao['correto'] and correcao['origemGabarito']=='GERADO_IA_NAO_OFICIAL'
        checks.append('Somente as quatro originais disponíveis; resolução sem gabarito oficial')
        if com_provedor:
            a=next(a for a in assuntos if a['nome']=='Ponteiros e passagem de endereços')
            sessao=cliente.chamar('POST','/api/v1/pratica/sessoes',dict(base,assuntoId=a['id'],nivelContexto='DETALHADO'),status=201)
            q=sessao['questoes'][0]
            correcao=cliente.chamar('POST',f"/api/v1/pratica/sessoes/{sessao['sessaoId']}/respostas",dict(questaoId=q['id'],alternativa='A'))
            assert 'Pseudocódigo de apoio' in correcao['resolucao']
            amostra=dict(questao=q,correcao=correcao)
            checks.append('Narrativa real do provedor com simulação e pseudocódigo preservados')
    finally:
        cliente.close()
        with store._conectar() as c:
            c.execute('DELETE FROM usuario WHERE email=%s AND nome=%s',[email,'Validação temporária ED básica'])
    relatorio=dict(aprovado=True,checks=checks,provedor_real_testado=com_provedor,conta_temporaria_removida=True,amostra=amostra)
    (ROOT/'output/verificacao-estrutura-de-dados.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(aprovado=True,checks=checks),ensure_ascii=True,indent=2))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--com-provedor',action='store_true');main(p.parse_args().com_provedor)
