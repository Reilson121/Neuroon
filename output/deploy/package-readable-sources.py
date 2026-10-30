import hashlib
import json
import tarfile
from pathlib import Path

root=Path(__file__).resolve().parents[2]
files=[f'frontend/src/components/{name}' for name in [
    'Texto.jsx','Monitor.jsx','referenciasLegiveis.js','RespostaMonitor.jsx','RespostaMonitor.css']]
output=root/'output/deploy'
manifest={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}
mp=output/'readable-sources-manifest.json'
mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with tarfile.open(output/'readable-sources-update.tar.gz','w:gz') as archive:
    for name in files: archive.add(root/name,arcname=name,recursive=False)
    archive.add(mp,arcname='readable-sources-manifest.json',recursive=False)
print('Pacote de apresentação:',len(files),'arquivos')
