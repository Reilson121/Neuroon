"""Aceitação HTTP local com usuários aleatórios removidos no finally.

Exige Spring:8080, FastAPI:8000 e corpus integrado. --com-provedor habilita
os testes reais do OpenRouter já autorizados pelo usuário. Nunca grava senhas,
cookies, chave interna ou dados pessoais da prova no relatório.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import uuid
from datetime import datetime,timezone
import httpx
from scripts.servicos_local import ambiente,ROOT,AI
from app.rag.vector_store import VectorStore


def hash_teste(senha,env):
    cache=Path(env.get('GRADLE_USER_HOME',str(Path.home()/'.gradle')))/'caches/modules-2/files-2.1'
    crypto=next((cache/'org.springframework.security/spring-security-crypto').rglob('*.jar'))
    logging=next((cache/'commons-logging/commons-logging').rglob('*.jar'))
    cp=os.pathsep.join(map(str,[crypto,logging]))
    result=subprocess.run([str(Path(env['JAVA_HOME'])/'bin/java.exe'),'--class-path',cp,
                           str(AI/'scripts/fixtures/HashSenhaTeste.java')],input=senha+'\n',
                          text=True,capture_output=True,env=env,check=True)
    saida=result.stdout.strip()
    if not saida.startswith('$2') or len(saida)!=60:raise RuntimeError('Codificação da senha de teste falhou.')
    return saida


class Cliente:
    def __init__(self):
        self.http=httpx.Client(base_url='http://127.0.0.1:8080',timeout=125)
        self.csrf=None
    def chamar(self,method,path,body=None,status=200):
        headers={}
        if method not in {'GET','HEAD'}:
            if self.csrf is None:self.csrf=self.chamar('GET','/api/v1/auth/csrf')
            headers[self.csrf['headerName']]=self.csrf['token']
        r=self.http.request(method,path,json=body,headers=headers)
        if r.status_code!=status:
            try:codigo=r.json().get('codigo','SEM_CODIGO')
            except Exception:codigo='SEM_CODIGO'
            raise AssertionError(f'{method} {path}: esperado {status}, recebido {r.status_code} ({codigo})')
        return r.json() if r.content else None
    def login(self,email,senha):
        r=self.chamar('POST','/api/v1/auth/login',{'email':email,'senha':senha})
        assert not any(k.lower().startswith('senha') for k in r)
        self.csrf=None;return r
    def close(self):self.http.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--com-provedor',action='store_true');args=parser.parse_args()
    env=ambiente();store=VectorStore();checks=[];usuarios=[];clientes=[];geradas=[];disciplina_teste=None;monitor_resposta=None
    def registrar(aprovado=False):
        report={'gerado_em_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'aprovado':aprovado,
                'provedor_real_testado':'geracao_real_e_cinco_correcoes_matematicas' in checks,'amostras_geradas':geradas,'monitor':monitor_resposta,'contas_temporarias_removidas':aprovado}
        (AI/'saidas_testes/estatistica_validacao_backend.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    def ok(nome):
        checks.append(nome);registrar();print(nome+': OK',flush=True)
    def alterar_material(mid,**campos):
        permitidos={'ativo','fonte_monitor_virtual','disponivel_para_pratica','autorizacao_professor'}
        if not campos or not set(campos)<=permitidos:raise ValueError('Campo inesperado no teste.')
        with store._conectar() as c:
            c.execute('UPDATE material SET '+','.join(k+'=%s' for k in campos)+' WHERE id=%s',[*campos.values(),mid])
    try:
        with httpx.Client(timeout=15) as interno:
            assert interno.post('http://127.0.0.1:8000/internal/v1/practice/questions',json={}).status_code==401
        ok('autenticacao_servico_interno')
        anon=Cliente();clientes.append(anon);anon.chamar('GET','/api/v1/periodos',status=401);ok('autenticacao_api_publica')
        senha=secrets.token_urlsafe(32);codificada=hash_teste(senha,env)
        for perfil in ['ESTUDANTE','ESTUDANTE','ADMINISTRADOR']:
            email='integracao-'+uuid.uuid4().hex+'@example.test'
            with store._conectar() as c:
                uid=c.execute("INSERT INTO usuario(nome,email,senha_hash,perfil) VALUES('Teste de integração',%s,%s,%s) RETURNING id",[email,codificada,perfil]).fetchone()[0]
            usuarios.append((uid,email));cli=Cliente();clientes.append(cli);cli.login(email,senha)
        aluno,outro,admin=clientes[1:]
        ps=aluno.chamar('GET','/api/v1/periodos');p=next(p for p in ps if p['numero']==3)
        ds=aluno.chamar('GET',f"/api/v1/periodos/{p['id']}/disciplinas");d=next(d for d in ds if d['nome']=='Estatística');did=d['id']
        assuntos=aluno.chamar('GET',f'/api/v1/disciplinas/{did}/assuntos');assert len(assuntos)==31
        materias=aluno.chamar('GET',f'/api/v1/disciplinas/{did}/materiais');assert len(materias)==3
        lista=next(m for m in materias if m['tipo']=='LISTA_EXERCICIOS');prova=next(m for m in materias if m['tipo']=='PROVA_ANTIGA')
        slides=next(m for m in materias if m['tipo']=='SLIDE_AULA')
        with store._conectar() as c:
            slugs=dict(c.execute('SELECT slug,id FROM assunto WHERE disciplina_id=%s',[did]).fetchall())
        ok('catalogo_periodo_disciplina_31_assuntos_3_materiais')
        with store._conectar() as c:
            disciplina_teste=c.execute("INSERT INTO disciplina(periodo_id,nome,slug) VALUES(%s,'Teste de integração',%s) RETURNING id",[p['id'],'teste_integracao_'+uuid.uuid4().hex]).fetchone()[0]
            assunto_teste=c.execute("INSERT INTO assunto(disciplina_id,nome,slug) VALUES(%s,'Assunto de teste','assunto_teste') RETURNING id",[disciplina_teste]).fetchone()[0]
        r=aluno.chamar('POST','/api/v1/pratica/sessoes',{'disciplinaId':did,'assuntoId':assunto_teste,'quantidade':5},status=400)
        assert r['codigo']=='ASSUNTO_DE_OUTRA_DISCIPLINA';ok('rejeita_assunto_de_outra_disciplina')
        perms={'ativo':True,'fonteMonitorVirtual':False,'disponivelParaPratica':True,'autorizacaoProfessor':True}
        aluno.chamar('PUT',f"/api/v1/admin/materiais/{lista['id']}",perms,status=403);ok('estudante_nao_altera_permissoes')
        def sessao(cli=aluno,**kwargs):
            esperado=kwargs.pop('_status',201)
            body={'disciplinaId':did,'quantidade':10,'modo':'CADASTRADAS','revisarVistas':True,**kwargs}
            return cli.chamar('POST','/api/v1/pratica/sessoes',body,status=esperado)
        base=sessao();assert len(base['questoes'])==6
        proibidos={'gabarito','alternativaCorreta','alternativa_correta','spec','resolucao','calculos'}
        for q in base['questoes']:
            assert not proibidos.intersection(q);assert q['origem']=='MATERIAL_ACADEMICO';assert len(q['alternativas'])==5;assert q['fontes']
        ok('seis_originais_sem_vazamento_de_gabarito')
        sid=base['sessaoId'];q=base['questoes'][0];answer={'questaoId':q['id'],'alternativa':'A'}
        path=f'/api/v1/pratica/sessoes/{sid}/respostas'
        outro.chamar('POST',path,answer,status=404)
        aluno.chamar('POST',f'/api/v1/pratica/sessoes/{uuid.uuid4()}/respostas',answer,status=404)
        aluno.chamar('POST',path,{**answer,'questaoId':str(uuid.uuid4())},status=400)
        aluno.chamar('POST',path,{**answer,'alternativa':'Z'},status=400)
        ok('isolamento_usuario_sessao_questao_e_alternativa')
        correcao=aluno.chamar('POST',path,answer)
        for campo in ['correto','alternativaCorreta','conceito','formula','calculos','resolucao','errosComuns','dica','origemGabarito','fontes']:assert campo in correcao
        assert correcao['correto']==('A'==correcao['alternativaCorreta']);assert correcao['aviso']
        assert aluno.chamar('POST',path,answer)==correcao
        aluno.chamar('POST',path,{**answer,'alternativa':'B'},status=409)
        ok('correcao_didatica_idempotencia_e_conflito')
        restantes=aluno.chamar('POST','/api/v1/pratica/sessoes',{'disciplinaId':did,'quantidade':10,'revisarVistas':False})
        assert restantes['estado']=='SEM_QUESTOES' and not restantes['questoes'];ok('reducao_de_repeticoes_e_estado_vazio')
        for origem,total in [('LISTA',4),('PROVA',6)]:
            s=sessao(origem=origem);assert len(s['questoes'])==total
            assert all(len(x['fontes'])==1 for x in s['questoes'])
        ok('filtros_por_lista_e_prova')
        with store._conectar() as c:
            v=json.loads(c.execute('SELECT embedding::text FROM chunk_documento WHERE material_id=%s LIMIT 1',[slides['id']]).fetchone()[0])
        assert store.buscar_similares(v,'estatistica',k=3)
        sem_vinculo='teste_integracao_'+uuid.uuid4().hex
        try:
            with store._conectar() as c:
                c.execute("""INSERT INTO chunk_documento(chunk_id,conteudo,embedding,periodo,disciplina,assunto,aula,arquivo,tipo_arquivo,tipo_extracao,pagina,chunk_index,metadata)
                    SELECT %s,conteudo,embedding,periodo,disciplina,assunto,aula,arquivo,tipo_arquivo,tipo_extracao,pagina,chunk_index,metadata-'material_id'
                    FROM chunk_documento WHERE material_id=%s LIMIT 1""",[sem_vinculo,slides['id']])
            alterar_material(slides['id'],fonte_monitor_virtual=False)
            assert not store.buscar_similares(v,'estatistica',k=3)
            ok('monitor_bloqueia_fonte_desativada_e_chunk_sem_vinculo')
        finally:
            alterar_material(slides['id'],fonte_monitor_virtual=slides['fonteMonitorVirtual'])
            with store._conectar() as c:c.execute('DELETE FROM chunk_documento WHERE chunk_id=%s',[sem_vinculo])
        a=slugs['medidas_de_tendencia_central'];s=sessao(assuntoId=a);assert len(s['questoes'])==1
        assert all('mediana' in x['enunciado'].lower() for x in s['questoes']);ok('filtro_por_assunto')
        for modo in ['CADASTRADAS','GERADAS_IA']:
            r=aluno.chamar('POST','/api/v1/pratica/sessoes',{'disciplinaId':did,'assuntoId':slugs['distribuicao_de_poisson'],'modo':modo,'quantidade':5})
            assert r['estado']=='SEM_QUESTOES' and not r['questoes']
        ok('assunto_sem_avaliacao_nao_recebe_questoes_artificiais')
        # Atualizações isoladas da fixture são restauradas mesmo se uma asserção falhar.
        try:
            alterar_material(lista['id'],disponivel_para_pratica=False,autorizacao_professor=False)
            alterar_material(prova['id'],disponivel_para_pratica=False,autorizacao_professor=False)
            aluno.chamar('POST',path,answer,status=409)
            r=aluno.chamar('POST','/api/v1/pratica/sessoes',{'disciplinaId':did,'quantidade':5,'modo':'GERADAS_IA'})
            assert not r['questoes'];ok('revogacao_bloqueia_inicio_e_correcao_imediatamente')
        finally:
            for m in [lista,prova]:alterar_material(m['id'],disponivel_para_pratica=m['disponivelParaPratica'],autorizacao_professor=m['autorizacaoProfessor'])
        with store._conectar() as c:c.execute('UPDATE disciplina SET possui_prova=FALSE WHERE id=%s',[did])
        try:
            r=aluno.chamar('POST','/api/v1/pratica/sessoes',{'disciplinaId':did,'quantidade':5},status=409)
            assert r['codigo']=='DISCIPLINA_SEM_PROVA';ok('disciplina_sem_prova_retorna_409')
        finally:
            with store._conectar() as c:c.execute('UPDATE disciplina SET possui_prova=TRUE WHERE id=%s',[did])
        admin.chamar('PUT',f"/api/v1/admin/materiais/{lista['id']}",perms,status=204)
        ok('administrador_sincroniza_material_sem_duplicacao')
        if args.com_provedor:
            # Chamada real: somente rótulos de conceitos são enviados na geração.
            s=sessao(cli=outro,modo='GERADAS_IA',assuntoId=slugs['medidas_de_dispersao_e_posicao'],quantidade=5)
            assert len(s['questoes'])==5 and all(q['origem']=='GERADA_IA' for q in s['questoes'])
            for q in s['questoes']:
                c=outro.chamar('POST',f"/api/v1/pratica/sessoes/{s['sessaoId']}/respostas",{'questaoId':q['id'],'alternativa':'A'})
                assert c['origemGabarito']=='GERADO_IA_VALIDADO_MATEMATICAMENTE'
                assert c['formula'] and c['substituicao'] and c['calculos'] and c['dica']
                geradas.append({'questao':q,'correcao':c})
            ok('geracao_real_e_cinco_correcoes_matematicas')
            nova=sessao(cli=outro,modo='GERADAS_IA',assuntoId=slugs['medidas_de_dispersao_e_posicao'],quantidade=1,revisarVistas=False)
            assert {q['fingerprint'] for q in nova['questoes']}.isdisjoint({q['fingerprint'] for q in s['questoes']})
            ok('nova_geracao_reduz_repeticoes')
            # SSE público: verifica resposta, disciplina, assunto e páginas citadas.
            outro.csrf=outro.chamar('GET','/api/v1/auth/csrf')
            pergunta='O que representa a mediana e como os valores extremos afetam a escolha da medida central?'
            r=outro.http.post('/api/v1/monitor/chat',headers={outro.csrf['headerName']:outro.csrf['token']},json={'disciplinaId':did,'assuntoId':slugs['medidas_de_tendencia_central'],'pergunta':pergunta})
            assert r.status_code==200 and 'text/event-stream' in r.headers['content-type']
            eventos={}
            for bloco in r.text.replace('\r\n','\n').split('\n\n'):
                linhas=bloco.splitlines();nome=next((l[6:].strip() for l in linhas if l.startswith('event:')),None)
                data='\n'.join(l[5:].strip() for l in linhas if l.startswith('data:'))
                if nome and data:eventos[nome]=json.loads(data)
            monitor_resposta={'pergunta':pergunta,'eventos':eventos};registrar()
            if 'error' in eventos:raise AssertionError('Monitor indisponível: '+eventos['error'].get('codigo','SEM_CODIGO'))
            assert 'done' in eventos and not eventos['done']['fallback'] and eventos['token']['texto']
            fontes=eventos['sources']['fontes'];assert fontes
            assert all(f['disciplina']=='estatistica' and f['assunto']=='medidas_de_tendencia_central' and f['tipo_material']=='SLIDE_AULA' and f['material_id'] for f in fontes)
            ok('monitor_publico_sse_com_fontes_corretas')
            conversa=eventos['done']['threadId']
            detalhe=outro.chamar('GET',f'/api/v1/monitor/conversas/{conversa}')
            assert len(detalhe['mensagens'])==2
            assert detalhe['mensagens'][0]['conteudo']==pergunta and detalhe['mensagens'][1]['fontes']==fontes
            lista_conversas=outro.chamar('GET',f"/api/v1/monitor/conversas?disciplinaId={did}&assuntoId={slugs['medidas_de_tendencia_central']}")
            assert any(c['id']==conversa for c in lista_conversas)
            ok('historico_persiste_pergunta_resposta_e_fontes')
            aluno.chamar('GET',f'/api/v1/monitor/conversas/{conversa}',status=404)
            assert not aluno.chamar('GET',f"/api/v1/monitor/conversas?disciplinaId={did}&assuntoId={slugs['medidas_de_tendencia_central']}")
            r=outro.chamar('POST','/api/v1/monitor/chat',{'disciplinaId':did,'assuntoId':slugs['fundamentos_de_probabilidade'],'pergunta':'O que é probabilidade?','threadId':conversa},status=400)
            assert r['codigo']=='CONTEXTO_DIFERENTE';ok('historico_isola_usuario_e_contexto')
            # A continuação também deve preservar uma recusa legítima, sem
            # atribuir referências dos slides a uma pergunta de outro domínio.
            pergunta2='Qual é a capital da França?'
            r=outro.http.post('/api/v1/monitor/chat',headers={outro.csrf['headerName']:outro.csrf['token']},json={'disciplinaId':did,'assuntoId':slugs['medidas_de_tendencia_central'],'pergunta':pergunta2,'threadId':conversa})
            assert r.status_code==200
            continuacao={}
            for bloco in r.text.replace('\r\n','\n').split('\n\n'):
                linhas=bloco.splitlines();nome=next((l[6:].strip() for l in linhas if l.startswith('event:')),None)
                data='\n'.join(l[5:].strip() for l in linhas if l.startswith('data:'))
                if nome and data:continuacao[nome]=json.loads(data)
            monitor_resposta['continuacao']=continuacao;registrar()
            assert continuacao['done']['threadId']==conversa
            assert continuacao['done']['fallback'] and not continuacao['sources']['fontes']
            detalhe=outro.chamar('GET',f'/api/v1/monitor/conversas/{conversa}')
            assert len(detalhe['mensagens'])==4 and detalhe['mensagens'][2]['conteudo']==pergunta2
            assert detalhe['mensagens'][3]['fontes']==continuacao['sources']['fontes']
            ok('historico_continua_conversa_e_preserva_ordem')
            outro.chamar('POST','/api/v1/auth/logout',status=204);outro.csrf=None
            outro.login(usuarios[1][1],senha)
            assert len(outro.chamar('GET',f'/api/v1/monitor/conversas/{conversa}')['mensagens'])==4
            ok('historico_reabre_apos_novo_login')
        aluno.chamar('POST','/api/v1/auth/logout',status=204);aluno.chamar('GET','/api/v1/auth/me',status=401);ok('logout_invalida_sessao')
    finally:
        for cli in clientes:cli.close()
        with store._conectar() as c:
            if c.execute("SELECT to_regclass('conversa_monitor')").fetchone()[0]:
                ids=[uid for uid,_ in usuarios]
                c.execute('DELETE FROM mensagem_monitor WHERE conversa_id IN (SELECT id FROM conversa_monitor WHERE usuario_id=ANY(%s))',[ids])
                c.execute('DELETE FROM conversa_monitor WHERE usuario_id=ANY(%s)',[ids])
            for uid,email in usuarios:c.execute("DELETE FROM usuario WHERE id=%s AND email=%s AND email LIKE 'integracao-%%@example.test'",[uid,email])
            if disciplina_teste is not None:
                c.execute('DELETE FROM assunto WHERE disciplina_id=%s',[disciplina_teste])
                c.execute("DELETE FROM disciplina WHERE id=%s AND slug LIKE 'teste_integracao_%%'",[disciplina_teste])
            if c.execute('SELECT count(*) FROM usuario WHERE id=ANY(%s)',[[uid for uid,_ in usuarios]]).fetchone()[0]:
                raise RuntimeError('Contas de teste não foram removidas.')
    registrar(True)
    print(json.dumps({'aprovado':True,'verificacoes':len(checks),'contas_temporarias_removidas':True},ensure_ascii=True),flush=True)

if __name__=='__main__':main()
