"""Prepara atualização incremental e registra as fontes atuais da VPS."""
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/deploy'
FILES=[
 'backend/demo/src/main/java/com/Neuron/demo/pratica/PraticaService.java',
 'frontend/src/App.jsx','frontend/src/hooks/useSessaoPratica.js',
 'frontend/src/components/DesignPratica.jsx','frontend/src/components/CalculoFiltros.jsx',
 'frontend/src/components/CalculoPratica.jsx',
 'neuron-ai/app/practice/calculo_engine.py','neuron-ai/app/practice/repository.py',
 'neuron-ai/app/practice/service.py','docs/CALCULO_COMPUTACAO_I.md',
]
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
before=OUT/'calculo-provas-before'
for name,value in remote.items():
 if value:
  p=before/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value['text'],encoding='utf-8')
manifest={name:dict(expected=remote[name]['sha256'] if remote[name] else None,sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()) for name in FILES}
mp=OUT/'calculo-provas-manifest.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with tarfile.open(OUT/'calculo-provas-update.tar.gz','w:gz') as tar:
 for name in FILES:tar.add(ROOT/name,arcname=name,recursive=False)
 tar.add(mp,arcname='calculo-provas-manifest.json',recursive=False)
print(json.dumps(dict(arquivos=len(FILES),bytes=(OUT/'calculo-provas-update.tar.gz').stat().st_size)))
