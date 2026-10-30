"""Prepara atualizaÃ§Ã£o incremental e registra as fontes atuais da VPS."""
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/deploy'
FILES=['neuron-ai/app/practice/math_presentation.py', 'neuron-ai/app/practice/service.py', 'neuron-ai/app/rag/monitor_virtual.py', 'frontend/src/App.jsx', 'frontend/src/components/Monitor.jsx', 'frontend/src/components/ApoioEstatistica.jsx', 'frontend/src/estatistica-paginas.json', 'frontend/src/components/Texto.css']
SSH=['ssh','-i','deploy/access/neuron_enuvem','-o','UserKnownHostsFile=deploy/access/known_hosts','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','root@45.159.173.74']
code='''import json,hashlib
from pathlib import Path
root=Path('/opt/neuron')
out={}
for name in NAMES:
 p=root/name
 out[name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),text=p.read_text()) if p.exists() else None
print(json.dumps(out))
'''.replace('NAMES',repr(FILES))
r=subprocess.run([*SSH,'python3 -'],input=code,text=True,encoding='utf-8',capture_output=True,cwd=ROOT)
if r.returncode:raise RuntimeError(r.stderr.strip())
remote=json.loads(r.stdout)
before=OUT/'math-global-before'
for name,value in remote.items():
 if value:
  p=before/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value['text'],encoding='utf-8')
stage=OUT/'math-global-stage'
def replace_once(text,old,new):
 if text.count(old)!=1:raise ValueError('Contexto de publicação divergente: '+old[:60])
 return text.replace(old,new,1)
for name in FILES:
 local=(ROOT/name).read_text(encoding='utf-8')
 text=local
 # Publica apenas esta alteração. Cálculo II tem trabalho paralelo local que
 # ainda não estava na VPS; não o habilita nem o sobrescreve aqui.
 if name.endswith('practice/service.py'):
  text=remote[name]['text']
  if 'from app.practice.math_presentation import present' not in text:text=replace_once(text,'from app.practice.math_engine import verificar','from app.practice.math_engine import verificar\nfrom app.practice.math_presentation import present')
  anchor='            segredos[qid] = q'
  if "q['_math_presentation']=" not in text:text=replace_once(text,anchor,"            q['_math_presentation']=any(r.get('disciplina_slug') in {'estatistica','calculo_para_computacao_1','calculo_para_computacao_2'} for r in refs)\n"+anchor)
  if '            publicas.append({k: q[k]' in text:text=replace_once(text,'            publicas.append({k: q[k]',"            view=present(q) if q['_math_presentation'] else q\n            publicas.append({k: view[k]")
  anchor='            s["respostas"][q["id"]] = (req["alternativa"], copy.deepcopy(correcao))'
  if "if q.get('_math_presentation')" not in text:text=replace_once(text,anchor,"            if q.get('_math_presentation'):\n                view=present(q)\n                for k in ['formula','substituicao','calculos','resolucao','erros_comuns','dica']:correcao[k]=view[k]\n"+anchor)
 if name.endswith('src/App.jsx'):
  text=remote[name]['text']
  if "import ApoioEstatistica" not in text:text=replace_once(text,"import CalculoFiltros from './components/CalculoFiltros.jsx';","import CalculoFiltros from './components/CalculoFiltros.jsx';\nimport ApoioEstatistica from './components/ApoioEstatistica.jsx';")
  if "{disciplina.nome==='Estatística'&&<ApoioEstatistica" not in text:text=replace_once(text,' {edBasica&&<p className="notice">'," {disciplina.nome==='Estatística'&&<ApoioEstatistica materiais={materiais} assuntos={assuntos} assuntoId={assuntoId}/>}\n {edBasica&&<p className=\"notice\">")
  if 'assuntoNome={assuntoNome} Fontes={Fontes}' in text:text=replace_once(text,'assuntoNome={assuntoNome} Fontes={Fontes}','assuntoNome={assuntoNome} materiais={materiais} assuntos={assuntos} Fontes={Fontes}')
 if name.endswith('rag/monitor_virtual.py'):
  opening='PROMPT_SISTEMA = r"""Você é o Monitor Virtual do NEURON, um tutor conversacional.\n'
  extra=local.split(opening,1)[1].split('Cálculo para Computação II',1)[0]
  text=remote[name]['text']
  if 'Em Estatística, Cálculo I e Cálculo II, escreva TODAS' not in text:text=replace_once(text,opening,opening+extra)
 p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
manifest={name:dict(expected=remote[name]['sha256'] if remote[name] else None,sha256=hashlib.sha256((stage/name).read_bytes()).hexdigest()) for name in FILES}
mp=OUT/'math-global-manifest.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with tarfile.open(OUT/'math-global-update.tar.gz','w:gz') as tar:
 for name in FILES:tar.add(stage/name,arcname=name,recursive=False)
 tar.add(mp,arcname='math-global-manifest.json',recursive=False)
print(json.dumps(dict(arquivos=len(FILES),bytes=(OUT/'math-global-update.tar.gz').stat().st_size)))
