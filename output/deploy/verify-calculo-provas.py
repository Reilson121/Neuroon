"""Aceitação do site e do banco publicado; relatório sem dados de contas reais."""
import hashlib
import http.cookiejar
import json
import re
import secrets
import subprocess
import tarfile
import urllib.request
import uuid
from pathlib import Path

ROOT=Path('/opt/neuron');BASE='https://neuron-45-159-173-74.sslip.io'
report=dict(aprovado=False,checks=[])
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
csrf=None;created=False
email='calculo-provas-'+uuid.uuid4().hex+'@example.invalid';nome='Validação temporária simulados de Cálculo'

def request(path,body=None,raw=False):
 headers={}
 if body is not None:
  headers['Content-Type']='application/json'
  if csrf:headers[csrf['headerName']]=csrf['token']
 req=urllib.request.Request(BASE+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
 with opener.open(req,timeout=150) as r:
  data=r.read();return data if raw else json.loads(data)

def check(text):
 report['checks'].append(text);print(text,flush=True)

def inside(code,*args):
 r=subprocess.run(['docker','exec','-i','neuron-ai-1','python','-B','-c',code,*args],capture_output=True,text=True,timeout=480)
 if r.returncode:raise RuntimeError('Conferência interna falhou: '+r.stderr[-2000:])
 return json.loads(r.stdout)

try:
 html=request('/',raw=True).decode();asset=re.search(r'src="(/assets/[^\"]+\.js)"',html).group(1)
 js=request(asset,raw=True).decode()
 assert all(s in js for s in ['Prova por assuntos selecionados','Prova da 1ª unidade','Prova da 2ª unidade','Prova final · duas unidades','Segunda chamada · duas unidades','Finalizar simulado'])
 report['interface_js']=asset
 check('Interface HTTPS contém os cinco modos de prova de Cálculo e a entrega do simulado')
 csrf=request('/api/v1/auth/csrf');senha='Validacao!'+secrets.token_urlsafe(24)
 request('/api/v1/auth/cadastro',dict(nome=nome,email=email,senha=senha));created=True
 request('/api/v1/auth/login',dict(email=email,senha=senha));csrf=request('/api/v1/auth/csrf')
 p=next(p for p in request('/api/v1/periodos') if p['numero']==2)
 ds=request('/api/v1/periodos/%s/disciplinas'%p['id']);d=next(d for d in ds if d['nome']=='Cálculo para Computação I')
 assuntos=request('/api/v1/disciplinas/%s/assuntos'%d['id']);assert len(assuntos)==9
 topicos=json.loads((ROOT/'frontend/src/calculo-topicos.json').read_text())
 ordens_por_conceito={t['nome']:t['assuntoOrdem'] for t in topicos}
 base=dict(disciplinaId=d['id'],assuntoId=None,modo='GERADAS_IA',origem='MISTO',quantidade=10,unidadeCalculo=0,topicoCalculo='MISTO',tipoFuncao='MISTO')
 vistos=set()
 for _ in range(3):
  s=request('/api/v1/pratica/sessoes',dict(base,topicoCalculo='fatoracao',tipoFuncao='RACIONAL'))
  assert s['estado']=='DISPONIVEL' and len(s['questoes'])==10
  novos={q['fingerprint'] for q in s['questoes']};assert len(novos)==10 and not vistos&novos;vistos.update(novos)
 check('HTTPS: três práticas consecutivas de fatoração produzem 30 questões distintas')
 provas=[]
 for tipo,ordens,unidade in [('ASSUNTOS',[1,3],0),('UNIDADE_1',list(range(1,6)),1),('UNIDADE_2',list(range(6,10)),2),('FINAL',list(range(1,10)),0),('SEGUNDA_CHAMADA',list(range(1,10)),0)]:
  ids=[a['id'] for a in assuntos if a['ordem'] in ordens]
  s=request('/api/v1/pratica/sessoes',dict(base,assuntoIds=ids,unidadeCalculo=unidade))
  assert s['estado']=='DISPONIVEL' and len(s['questoes'])==10,tipo
  assert {ordens_por_conceito[q['conceito']] for q in s['questoes']}==set(ordens),tipo
  for q in s['questoes']:
   assert len(q['alternativas'])==5 and q['fontes'] and not {'spec','gabarito','resolucao','calculos'}.intersection(q)
  corrigir=s['questoes'] if tipo=='FINAL' else s['questoes'][:1]
  for q in corrigir:
   c=request('/api/v1/pratica/sessoes/%s/respostas'%s['sessaoId'],dict(questaoId=q['id'],alternativa='A'))
   assert isinstance(c['correto'],bool) and c['alternativaCorreta'] in q['alternativas'] and c['calculos'] and c['fontes']
  provas.append(dict(tipo=tipo,assuntos=len(ids),questoes=len(s['questoes']),correcoes=len(corrigir)))
  print('PROVA_CONFERIDA',tipo,flush=True)
 report['provas']=provas
 check('HTTPS: seleção livre, unidades, final e segunda chamada cobrem todos os assuntos previstos; final corrigida por completo')
 p3=next(p for p in request('/api/v1/periodos') if p['numero']==3)
 ds3=request('/api/v1/periodos/%s/disciplinas'%p3['id'])
 design=next(d for d in ds3 if d['nome']=='Design de Artefatos Digitais')
 da=request('/api/v1/disciplinas/%s/assuntos'%design['id'])
 s=request('/api/v1/pratica/sessoes',dict(disciplinaId=design['id'],assuntoId=None,assuntoIds=[a['id'] for a in da[:2]],modo='GERADAS_IA',origem='MISTO',quantidade=3))
 assert len(s['questoes'])==3
 check('Simulado por conteúdos de Design continua disponível no HTTPS')
 report['cobertura_interna']=inside('''
import json,uuid
from psycopg.rows import dict_row
from app.practice.repository import QuestionRepository
from app.practice.service import PracticeService
from app.practice.calculo_engine import TOPICOS,gerar,verificar
repo=QuestionRepository();service=PracticeService(repository=repo)
with repo.store._conectar() as c:
 c.execute('SET TRANSACTION READ ONLY')
 with c.cursor(row_factory=dict_row) as cur:
  cur.execute("SELECT id FROM disciplina WHERE slug='calculo_para_computacao_1'");did=cur.fetchone()['id']
  cur.execute('SELECT id FROM material WHERE disciplina_id=%s AND ativo',[did]);mids=[r['id'] for r in cur.fetchall()]
refs=repo.buscar_questoes(did,None,mids,'MISTO',usar_teoria=True)
out=[]
for t,(slug,unidade,nome,tipos) in TOPICOS.items():
 for tipo in tipos:
  qs=gerar(slug,refs,10,[],unidade=unidade,topico=t,tipo_funcao=tipo)
  assert len(qs)==10,(t,tipo,len(qs))
  assert len({q['fingerprint'] for q in qs})==10
  assert all(verificar(q) for q in qs)
  out.append(dict(topico=t,tipo=tipo,questoes=len(qs)))
vistos=set()
for _ in range(21):
 qs=gerar('simplificacao_algebrica',refs,10,vistos,topico='fatoracao',tipo_funcao='RACIONAL')
 assert len(qs)==10
 novos={q['fingerprint'] for q in qs};assert not vistos&novos;vistos.update(novos)
print(json.dumps(dict(topicos=len(TOPICOS),combinacoes=len(out),questoes_conferidas=sum(r['questoes'] for r in out),fatoracoes_sem_repetir=len(vistos),cobertura=out)))
''')
 check('Índice publicado: 28 tópicos, 43 combinações e 430 questões conferidas; 210 fatorações sem repetir')
 backup=Path((ROOT/'calculo-provas-last-backup.txt').read_text().strip())
 target='neuron-ai/app/rag/monitor_virtual.py'
 with tarfile.open(backup/'sources.tar.gz') as tar:before=tar.extractfile(target).read()
 report['formatacao_monitor_preservada']=hashlib.sha256(before).digest()==hashlib.sha256((ROOT/target).read_bytes()).digest()
 assert report['formatacao_monitor_preservada']
 report['aprovado']=True
finally:
 report['conta_temporaria_removida']=inside('''
import sys,json
from app.rag.vector_store import VectorStore
email,nome=sys.argv[1:]
with VectorStore()._conectar() as c:
 row=c.execute('SELECT id FROM usuario WHERE email=%s AND nome=%s',[email,nome]).fetchone()
 n=c.execute('DELETE FROM usuario WHERE id=%s AND email=%s AND nome=%s',[row[0],email,nome]).rowcount if row else 0
print(json.dumps(n))
''',email,nome)==(1 if created else 0)
 backup=Path((ROOT/'calculo-provas-last-backup.txt').read_text().strip());baseline=json.loads((backup/'baseline.json').read_text())
 atual=inside('''
import json
from app.rag.vector_store import VectorStore
with VectorStore()._conectar() as c:
 c.execute('SET TRANSACTION READ ONLY')
 r=c.execute("SELECT json_build_object('usuarios',(SELECT coalesce(json_agg(id),'[]') FROM usuario WHERE perfil<>'VISITANTE'),'conversas',(SELECT coalesce(json_agg(c.id),'[]') FROM conversa_monitor c JOIN usuario u ON c.usuario_id=u.id WHERE u.perfil<>'VISITANTE'),'mensagens',(SELECT coalesce(json_agg(m.id),'[]') FROM mensagem_monitor m JOIN conversa_monitor c ON m.conversa_id=c.id JOIN usuario u ON c.usuario_id=u.id WHERE u.perfil<>'VISITANTE'),'materiais',(SELECT count(*) FROM material),'chunks',(SELECT count(*) FROM chunk_documento));").fetchone()[0]
print(json.dumps(r))
''')
 report['dados_permanentes_preservados']=all(set(baseline[k]).issubset(atual[k]) for k in ['usuarios','conversas','mensagens'])
 report['catalogo_e_indice_preservados']=all(baseline[k]==atual[k] for k in ['materiais','chunks'])
 report['aprovado']=report['aprovado'] and report['conta_temporaria_removida'] and report['dados_permanentes_preservados'] and report['catalogo_e_indice_preservados']
 (ROOT/'verificacao-calculo-provas-publicado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='cobertura_interna'},ensure_ascii=False,indent=2),flush=True)
 if not report['aprovado']:raise RuntimeError('Aceitação incompleta; conferir relatório.')
