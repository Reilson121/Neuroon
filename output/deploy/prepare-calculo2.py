import hashlib,json,subprocess,tarfile
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/deploy'
FILES=[
 'backend/demo/src/main/java/com/Neuron/demo/pratica/PraticaService.java',
 'backend/demo/src/main/resources/db/migration/V13__catalogo_calculo_2.sql',
 'frontend/src/App.jsx','frontend/src/components/CalculoFiltros.jsx','frontend/src/components/CalculoPratica.jsx','frontend/src/integral-topicos.json',
 'neuron-ai/app/practice/service.py','neuron-ai/app/practice/math_engine.py','neuron-ai/app/practice/material_index.py','neuron-ai/app/practice/repository.py','neuron-ai/app/practice/integral_engine.py',
 'neuron-ai/app/rag/monitor_virtual.py','neuron-ai/app/rag/retriever.py','neuron-ai/app/rag/integral_corpus.py','neuron-ai/app/rag/integral_search.py',
 'neuron-ai/scripts/integrar_materiais_calculo2.py','deploy/Dockerfile.ai','docs/CALCULO_COMPUTACAO_II.md',
]
FILES += [p.relative_to(ROOT).as_posix() for p in (ROOT/'neuron-ai/materiais_academicos/periodo_03/calculo_para_computacao_2').iterdir() if p.is_file()]
SSH=['ssh','-i','deploy/access/neuron_enuvem','-o','UserKnownHostsFile=deploy/access/known_hosts','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','root@45.159.173.74']
code='''import json,hashlib
from pathlib import Path
root=Path('/opt/neuron');out={}
for name in NAMES:
 p=root/name
 out[name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),text=p.read_text() if p.suffix not in {'.pdf'} else None) if p.exists() else None
print(json.dumps(out))
'''.replace('NAMES',repr(FILES))
r=subprocess.run([*SSH,'python3 -'],input=code,text=True,encoding='utf-8',capture_output=True,cwd=ROOT,timeout=70)
if r.returncode:raise RuntimeError(r.stderr.strip())
remote=json.loads(r.stdout)
for name,value in remote.items():
 if value and value['text'] is not None:
  p=OUT/'calculo2-before'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value['text'],encoding='utf-8')
staged=OUT/'calculo2-staged'
for name in FILES:
 if '--reuse-staged' in sys.argv:continue
 data=(ROOT/name).read_bytes()
 if not name.endswith('.pdf'):data=data.decode('utf-8').replace('\r\n','\n').encode('utf-8')
 if name=='frontend/src/App.jsx':
  text=data.decode('utf-8').replace("import ApoioEstatistica from './components/ApoioEstatistica.jsx';\n",'')
  text='\n'.join(line for line in text.split('\n') if "{disciplina.nome==='Estatística'&&<ApoioEstatistica" not in line)
  text=text.replace('assuntoNome={assuntoNome} materiais={materiais} assuntos={assuntos} Fontes={Fontes}','assuntoNome={assuntoNome} Fontes={Fontes}')
  data=text.encode('utf-8')
 if name=='neuron-ai/app/practice/service.py':
  text=data.decode('utf-8').replace('from app.practice.math_presentation import present\n','')
  text=text.replace("            q['_math_presentation']=any(r.get('disciplina_slug') in {'estatistica','calculo_para_computacao_1','calculo_para_computacao_2'} for r in refs)\n",'')
  text=text.replace("            view=present(q) if q['_math_presentation'] else q\n",'').replace('publicas.append({k: view[k]','publicas.append({k: q[k]')
  text=text.replace("            if q.get('_math_presentation'):\n                view=present(q)\n                for k in ['formula','substituicao','calculos','resolucao','erros_comuns','dica']:correcao[k]=view[k]\n",'')
  data=text.encode('utf-8')
 if name=='neuron-ai/app/rag/monitor_virtual.py':
  text=data.decode('utf-8');start=text.index('Em Estatística, Cálculo I e Cálculo II, escreva TODAS');end=text.index('Cálculo para Computação II (calculo_para_computacao_2) é do TERCEIRO período.')
  text=text[:start]+text[end:];data=text.encode('utf-8')
 target=staged/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
manifest={name:dict(expected=remote[name]['sha256'] if remote[name] else None,sha256=hashlib.sha256((staged/name).read_bytes()).hexdigest()) for name in FILES}
mp=OUT/'calculo2-manifest.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with tarfile.open(OUT/'calculo2-update.tar.gz','w:gz') as tar:
 for name in FILES:tar.add(staged/name,arcname=name,recursive=False)
 tar.add(mp,arcname='calculo2-manifest.json',recursive=False)
print(json.dumps(dict(arquivos=len(FILES),alterados=[n for n,m in manifest.items() if m['expected']!=m['sha256']],bytes=(OUT/'calculo2-update.tar.gz').stat().st_size),ensure_ascii=False))
