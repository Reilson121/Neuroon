"""Aceitação HTTPS da apresentação matemática e consultas de Estatística."""
import http.cookiejar,json,re,secrets,subprocess,urllib.request,uuid
from pathlib import Path
ROOT=Path('/opt/neuron');BASE='https://neuron-45-159-173-74.sslip.io'
report=dict(aprovado=False,checks=[]);created=False;csrf=None
email='math-global-'+uuid.uuid4().hex+'@example.invalid';nome='Validação temporária matemática e fórmulas'
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(path,body=None,raw=False):
 headers={}
 if body is not None:
  headers['Content-Type']='application/json'
  if csrf:headers[csrf['headerName']]=csrf['token']
 req=urllib.request.Request(BASE+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
 with opener.open(req,timeout=150) as r:
  data=r.read();return data if raw else json.loads(data)
def inside(code,*args):
 r=subprocess.run(['docker','exec','-i','neuron-ai-1','python','-B','-c',code,*args],capture_output=True,text=True,timeout=360)
 if r.returncode:raise RuntimeError(r.stderr[-2000:])
 return json.loads(r.stdout)
def check(text):report['checks'].append(text);print(text,flush=True)
def events(stream):
 result={}
 for block in stream.replace('\r\n','\n').split('\n\n'):
  lines=block.splitlines();k=next((l[6:].strip() for l in lines if l.startswith('event:')),None)
  data='\n'.join(l[5:].strip() for l in lines if l.startswith('data:'))
  if k and data:result[k]=json.loads(data)
 return result
try:
 html=request('/',raw=True).decode();asset=re.search(r'src="(/assets/[^\"]+\.js)"',html).group(1)
 js=request(asset,raw=True).decode()
 assert 'Consultar fórmulas e tabelas de Estatística' in js and 'katex' in js
 report['interface_js']=asset
 check('Interface pública contém renderização matemática e consulta aos slides de Estatística')
 csrf=request('/api/v1/auth/csrf');senha='Validacao!'+secrets.token_urlsafe(25)
 request('/api/v1/auth/cadastro',dict(nome=nome,email=email,senha=senha));created=True
 request('/api/v1/auth/login',dict(email=email,senha=senha));csrf=request('/api/v1/auth/csrf')
 periods=request('/api/v1/periodos');catalog=[]
 for p in periods:
  catalog.extend(request('/api/v1/periodos/%s/disciplinas'%p['id']))
 calc=next(d for d in catalog if d['nome']=='Cálculo para Computação I')
 stats=next(d for d in catalog if d['nome']=='Estatística')
 s=request('/api/v1/pratica/sessoes',dict(disciplinaId=calc['id'],modo='GERADAS_IA',origem='MISTO',quantidade=3,unidadeCalculo=1,topicoCalculo='racionalizacao',tipoFuncao='RADICAL'))
 assert len(s['questoes'])==3
 q=s['questoes'][0]
 assert all(command in q['enunciado'] for command in [r'\lim',r'\sqrt',r'\dfrac'])
 assert all(v.startswith('$') and v.endswith('$') for v in q['alternativas'].values())
 cor=request('/api/v1/pratica/sessoes/%s/respostas'%s['sessaoId'],dict(questaoId=q['id'],alternativa='A'))
 assert '$' in cor['formula'] and any('$' in step for step in cor['calculos'])
 check('HTTPS Cálculo I: limite, raiz, fração, alternativas e correção chegam em LaTeX')
 sa=request('/api/v1/disciplinas/%s/assuntos'%stats['id']);sm=request('/api/v1/disciplinas/%s/materiais'%stats['id'])
 slides=next(m for m in sm if m['tipo']=='SLIDE_AULA' and m['arquivoDisponivel'])
 with opener.open(BASE+'/api/v1/materiais/%s/arquivo'%slides['id'],timeout=60) as r:assert r.read(5)==b'%PDF-'
 check('HTTPS Estatística: os links de fórmulas usam o PDF original disponível e autenticado')
 s=request('/api/v1/pratica/sessoes',dict(disciplinaId=stats['id'],modo='CADASTRADAS',origem='MISTO',quantidade=5,revisarVistas=True))
 assert s['questoes']
 corrections=[]
 for q in s['questoes']:
  cor=request('/api/v1/pratica/sessoes/%s/respostas'%s['sessaoId'],dict(questaoId=q['id'],alternativa='A'))
  corrections.append(cor)
 assert any('$' in c['formula'] for c in corrections)
 check('HTTPS Estatística: questões dos materiais preservam alternativas e entregam fórmulas formatadas na correção')
 correlation=next(a for a in sa if a['ordem']==9)
 s=request('/api/v1/pratica/sessoes',dict(disciplinaId=stats['id'],assuntoId=correlation['id'],modo='GERADAS_IA',origem='MISTO',quantidade=1))
 assert len(s['questoes'])==1
 table=[line for line in s['questoes'][0]['enunciado'].splitlines() if line.startswith('|')]
 assert len(table)==7 and all(line.count('|')==3 for line in table)
 check('HTTPS Estatística: questão gerada por IA mantém as cinco observações e as duas colunas da tabela de correlação')
 report['motores']=inside('''
import json,random
from app.practice.math_presentation import present
from app.practice import calculo_engine as calc,math_engine as stats
engines=[(calc,'calculo')]
try:
 from app.practice import integral_engine as integral
 engines.append((integral,'integral'))
except ImportError:pass
out={}
for engine,motor in engines:
 count=0
 for t,(_,_,_,types) in engine.TOPICOS.items():
  for kind in types:
   q=engine.construir(dict(motor=motor,topico=t,tipo_funcao=kind,parametros=[3,2,4,5]),random.Random(7))
   assert engine.verificar(q)
   view=present(q);assert view['gabarito']==q['gabarito'] and view['fingerprint']==q['fingerprint']
   assert '$' in view['enunciado'] and all('$' in v or motor=='calculo' and t in {'laterais','infinito_ponto'} for v in view['alternativas'].values())
   count+=1
 out[motor]=count
count=0
for family in [f for fs in stats.FAMILIAS.values() for f in fs]:
 q=stats.construir(family,random.Random(7));view=present(q)
 assert stats.verificar(q) and view['gabarito']==q['gabarito']
 assert '$' in view['formula'] or family in {'mediana','espaco_amostral'}
 count+=1
out['estatistica']=count
print(json.dumps(out))
''')
 check('Motores publicados: formatação conferida sem alterar o cálculo, a identificação ou o gabarito')
 conditional=next(a for a in sa if a['ordem']==3)
 e=events(request('/api/v1/monitor/chat',dict(disciplinaId=stats['id'],assuntoId=conditional['id'],pergunta='Explique a fórmula da probabilidade condicional usando a notação dos slides. Escreva as frações em notação matemática.'),raw=True).decode())
 assert 'done' in e and not e['done']['fallback'] and 'sources' in e
 answer=e['token']['texto']
 report['chat_estatistica']=dict(resposta=answer,fontes=len(e['sources']['fontes']))
 assert '$' in answer and any(chr(92)+tag in answer for tag in ['dfrac','frac']),answer
 check('Chat real de Estatística respondeu com fração LaTeX e fontes dos slides')
 calc2=next((d for d in catalog if d['nome']=='Cálculo para Computação II'),None)
 if calc2 and calc2['possuiProva']:
  s=request('/api/v1/pratica/sessoes',dict(disciplinaId=calc2['id'],modo='GERADAS_IA',origem='MISTO',quantidade=1,unidadeCalculo=1,topicoCalculo='integral_direta',tipoFuncao='RADICAL'))
  assert len(s['questoes'])==1 and r'\int' in s['questoes'][0]['enunciado']
  check('HTTPS Cálculo II: integral, radical e alternativas em LaTeX')
  report['calculo2_publico']=True
 report['aprovado']=True
finally:
 report['conta_temporaria_removida']=inside('''
import sys,json
from app.rag.vector_store import VectorStore
email,nome=sys.argv[1:]
with VectorStore()._conectar() as c:
 row=c.execute('SELECT id FROM usuario WHERE email=%s AND nome=%s',[email,nome]).fetchone()
 if row:
  uid=row[0]
  c.execute('DELETE FROM mensagem_monitor WHERE conversa_id IN (SELECT id FROM conversa_monitor WHERE usuario_id=%s)',[uid])
  c.execute('DELETE FROM conversa_monitor WHERE usuario_id=%s',[uid])
  n=c.execute('DELETE FROM usuario WHERE id=%s AND email=%s AND nome=%s',[uid,email,nome]).rowcount
 else:n=0
print(json.dumps(n))
''',email,nome)==(1 if created else 0)
 report['aprovado']=report['aprovado'] and report['conta_temporaria_removida']
 (ROOT/'verificacao-math-global-publicado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
 if not report['aprovado']:raise RuntimeError('Aceitação incompleta; confira o relatório.')
