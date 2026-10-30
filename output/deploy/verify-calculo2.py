"""Aceitação pelo HTTPS público; não exporta contas ou conversas existentes."""
import hashlib,http.cookiejar,json,re,secrets,subprocess,time,urllib.request,uuid,sys
from pathlib import Path
ROOT=Path('/opt/neuron');BASE='https://neuron-45-159-173-74.sslip.io'
report=json.loads((ROOT/'verificacao-calculo2-publicado.json').read_text()) if '--monitor-only' in sys.argv else dict(checks=[]);report['aprovado']=False;csrf=None;created=False
email='calculo2-'+uuid.uuid4().hex+'@example.invalid';nome='Validação temporária Cálculo II'
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(path,body=None,raw=False):
 headers={}
 if body is not None:
  headers['Content-Type']='application/json'
  if csrf:headers[csrf['headerName']]=csrf['token']
 req=urllib.request.Request(BASE+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
 with opener.open(req,timeout=160) as r:
  data=r.read();return data if raw else json.loads(data)
def check(text):report['checks'].append(text);print(text,flush=True)
def inside(code,*args):
 r=subprocess.run(['docker','exec','-i','neuron-ai-1','python','-B','-c',code,*args],capture_output=True,text=True,timeout=240)
 if r.returncode:raise RuntimeError(r.stderr[-2000:])
 return json.loads(r.stdout)
def events(stream):
 out={}
 for block in stream.replace('\r\n','\n').split('\n\n'):
  kind=None;data=[]
  for line in block.splitlines():
   if line.startswith('event:'):kind=line[6:].strip()
   if line.startswith('data:'):data.append(line[5:].strip())
  if kind and data:out[kind]=json.loads('\n'.join(data))
 return out
try:
 html=request('/',raw=True).decode();asset=re.search(r'src="(/assets/[^\"]+\.js)"',html).group(1);js=request(asset,raw=True).decode()
 assert all(v in js for v in ['Cálculo para Computação II','Abrir tabela de integrais','Integrais duplas e triplas','Finalizar simulado'])
 report['interface_js']=asset;check('Interface HTTPS contém Cálculo II, tabela de integrais e simulados')
 csrf=request('/api/v1/auth/csrf');senha='Validacao!'+secrets.token_urlsafe(24)
 request('/api/v1/auth/cadastro',dict(nome=nome,email=email,senha=senha));created=True
 request('/api/v1/auth/login',dict(email=email,senha=senha));csrf=request('/api/v1/auth/csrf')
 ps=request('/api/v1/periodos');p3=next(p for p in ps if p['numero']==3)
 ds=request('/api/v1/periodos/%s/disciplinas'%p3['id']);d=next(d for d in ds if d['nome']=='Cálculo para Computação II');did=d['id']
 assert d['possuiProva'] and d['periodoId']==p3['id']
 assuntos=request('/api/v1/disciplinas/%s/assuntos'%did);materiais=request('/api/v1/disciplinas/%s/materiais'%did)
 assert len(assuntos)==8 and len(materiais)==4;report['disciplina_id']=did
 mids={m['id'] for m in materiais};manifest=json.loads((ROOT/'calculo2-manifest.json').read_text())
 for m in materiais:
  assert m['arquivoDisponivel'];data=request('/api/v1/materiais/%s/arquivo'%m['id'],raw=True)
  name=next(n for n in manifest if n.endswith('/'+m['titulo']+'.pdf'))
  assert data.startswith(b'%PDF') and hashlib.sha256(data).hexdigest()==manifest[name]['sha256']
 check('Cálculo II disponível no 3º período, com oito assuntos e quatro PDFs conferidos por hash')
 topicos=json.loads((ROOT/'frontend/src/integral-topicos.json').read_text());ordens={t['nome']:t['assuntoOrdem'] for t in topicos}
 base=dict(disciplinaId=did,assuntoId=None,modo='GERADAS_IA',origem='MISTO',quantidade=1,revisarVistas=True,unidadeCalculo=0,topicoCalculo='MISTO',tipoFuncao='MISTO')
 if '--monitor-only' not in sys.argv:
  amostras=[]
  for t in topicos:
   a=next(a for a in assuntos if a['ordem']==t['assuntoOrdem'])
   for tipo in t['tipos']:
    ss=request('/api/v1/pratica/sessoes',dict(base,assuntoId=a['id'],unidadeCalculo=t['unidade'],topicoCalculo=t['id'],tipoFuncao=tipo))
    assert ss['estado']=='DISPONIVEL' and len(ss['questoes'])==1,(t['id'],tipo,ss)
    q=ss['questoes'][0];assert len(q['alternativas'])==5 and q['fontes'] and not {'gabarito','spec','calculos','resolucao'}.intersection(q)
    assert all(f['materialId'] in mids for f in q['fontes'])
    c=request('/api/v1/pratica/sessoes/%s/respostas'%ss['sessaoId'],dict(questaoId=q['id'],alternativa='A'))
    assert isinstance(c['correto'],bool) and c['alternativaCorreta'] in q['alternativas'] and len(c['calculos'])>=3 and 'Tabela de Integrais' in c['dica']
    amostras.append(dict(topico=t['id'],tipo=tipo,unidade=t['unidade'],passos=len(c['calculos'])))
  report['topicos']=amostras;check('Geração e correção pelo HTTPS em todas as combinações de tópicos e funções de integrais')
  provas=[]
  for nome_prova,os,u in [('ASSUNTOS',[1,3],0),('UNIDADE_1',[1,2,3],1),('UNIDADE_2',[4,5,6,7],2),('FINAL',list(range(1,8)),0),('SEGUNDA_CHAMADA',list(range(1,8)),0)]:
   ids=[a['id'] for a in assuntos if a['ordem'] in os]
   ss=request('/api/v1/pratica/sessoes',dict(base,quantidade=10,assuntoIds=ids,unidadeCalculo=u))
   assert len(ss['questoes'])==10 and {ordens[q['conceito']] for q in ss['questoes']}==set(os),nome_prova
   q=ss['questoes'][0];c=request('/api/v1/pratica/sessoes/%s/respostas'%ss['sessaoId'],dict(questaoId=q['id'],alternativa='A'));assert c['calculos']
   provas.append(dict(tipo=nome_prova,questoes=10,assuntos=len(ids)))
  report['provas']=provas
  ss=request('/api/v1/pratica/sessoes',dict(base,quantidade=10));assert all(ordens[q['conceito']]<8 for q in ss['questoes'])
  ss=request('/api/v1/pratica/sessoes',dict(base,unidadeCalculo=1,topicoCalculo='dupla_retangulo'));assert ss['estado']=='SEM_QUESTOES'
  check('Simulados por unidade, seleção livre, final e segunda chamada funcionam; complemento não entra automaticamente e unidade 1 recusa duplas')
 monitor=[]
 for pergunta,ordem in [('Calcule a integral indefinida de 6x^2+4x-3, mostre os passos e indique a tabela de consulta.',2),('Calcule a integral de x+2y com y de 0 a 2 e x de 0 a 1, na ordem dy dx. Mostre cada etapa.',4),('Explique o que é uma função de duas variáveis e calcule f(1,2) para f(x,y)=x^2+y.',8)]:
  a=next(a for a in assuntos if a['ordem']==ordem);inicio=time.monotonic()
  e=events(request('/api/v1/monitor/chat',dict(disciplinaId=did,assuntoId=a['id'],pergunta=pergunta),raw=True).decode())
  assert 'done' in e and 'error' not in e and not e['done']['fallback'],(ordem,e)
  fontes=e.get('sources',{}).get('fontes');assert fontes
  monitor.append(dict(pergunta=pergunta,resposta=e['token']['texto'],fontes=fontes,segundos=round(time.monotonic()-inicio,2)))
  print('MONITOR_CONFERIDO',ordem,flush=True)
 report['monitor']=monitor;check('IA real pelo site respondeu sobre integral simples, dupla e complemento opcional, com fontes')
 p2=next(p for p in ps if p['numero']==2);d1=next(d for d in request('/api/v1/periodos/%s/disciplinas'%p2['id']) if d['nome']=='Cálculo para Computação I')
 ss=request('/api/v1/pratica/sessoes',dict(base,disciplinaId=d1['id'],unidadeCalculo=2,topicoCalculo='cadeia',tipoFuncao='POLINOMIAL'));assert len(ss['questoes'])==1
 check('Prática de Cálculo I continua funcionando')
 report['aprovado']=True
finally:
 report['conta_temporaria_removida']=inside('''
import json,sys
from app.rag.vector_store import VectorStore
email,nome=sys.argv[1:]
with VectorStore()._conectar() as c:
 row=c.execute('SELECT id FROM usuario WHERE email=%s AND nome=%s',[email,nome]).fetchone()
 n=0
 if row:
  uid=row[0]
  c.execute('DELETE FROM mensagem_monitor m USING conversa_monitor c WHERE m.conversa_id=c.id AND c.usuario_id=%s',[uid])
  c.execute('DELETE FROM conversa_monitor WHERE usuario_id=%s',[uid])
  n=c.execute('DELETE FROM usuario WHERE id=%s AND email=%s AND nome=%s',[uid,email,nome]).rowcount
print(json.dumps(n))
''',email,nome)==(1 if created else 0)
 backup=Path('/opt/neuron/deploy/backups/calculo2-20261030T022808Z');baseline=json.loads((backup/'baseline.json').read_text())
 atual=inside('''
import json
from app.rag.vector_store import VectorStore
with VectorStore()._conectar() as c:
 c.execute('SET TRANSACTION READ ONLY')
 r=c.execute("SELECT json_build_object('usuarios',(SELECT coalesce(json_agg(id),'[]') FROM usuario WHERE perfil<>'VISITANTE'),'conversas',(SELECT coalesce(json_agg(c.id),'[]') FROM conversa_monitor c JOIN usuario u ON c.usuario_id=u.id WHERE u.perfil<>'VISITANTE'),'mensagens',(SELECT coalesce(json_agg(m.id),'[]') FROM mensagem_monitor m JOIN conversa_monitor c ON m.conversa_id=c.id JOIN usuario u ON c.usuario_id=u.id WHERE u.perfil<>'VISITANTE'),'materiais',(SELECT count(*) FROM material),'chunks',(SELECT count(*) FROM chunk_documento));").fetchone()[0]
print(json.dumps(r))
''')
 report['dados_permanentes_preservados']=all(set(baseline[k]).issubset(atual[k]) for k in ['usuarios','conversas','mensagens'])
 report['acrescimos']=dict(materiais=atual['materiais']-baseline['materiais'],chunks=atual['chunks']-baseline['chunks'])
 report['aprovado']=report['aprovado'] and report['conta_temporaria_removida'] and report['dados_permanentes_preservados'] and report['acrescimos']==dict(materiais=4,chunks=216)
 (ROOT/'verificacao-calculo2-publicado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in {'topicos','monitor'}},ensure_ascii=False,indent=2),flush=True)
 if not report['aprovado']:raise RuntimeError('Aceitação incompleta; conferir relatório.')
