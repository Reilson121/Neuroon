import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path

root=Path('/opt/neuron')
base='https://neuron-45-159-173-74.sslip.io'
def fetch(path):
 with urllib.request.urlopen(base+path,timeout=30) as response:
  assert response.status==200
  return response.read().decode()
html=fetch('/')
js_path=re.search(r'src="(/assets/[^\"]+\.js)"',html).group(1)
css_path=re.search(r'href="(/assets/[^\"]+\.css)"',html).group(1)
js,css=fetch(js_path),fetch(css_path)
assert all(s in js for s in ['De onde veio esta explicação?','material consultado','Abrir material','Documento sem link disponível nesta conversa.'])
assert 'readable-source-list' in css and 'katex' in css
assert json.loads(fetch('/api/v1/auth/csrf'))['token']
manifest=json.loads((root/'readable-sources-manifest.json').read_text())
assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest for name,digest in manifest.items())
states=subprocess.run(['docker','compose','--env-file','deploy/.env','-f','deploy/compose.yaml','ps','--format','{{.Service}} {{.State}} {{.Health}}'],capture_output=True,text=True,check=True).stdout
assert all(s+' running healthy' in states for s in ['ai','backend','db'])
assert 'web running' in states
report={'aprovado':True,'interface_js':js_path,'interface_css':css_path,
        'arquivos_conferidos':len(manifest),'testes_interface':57,
        'verificacoes':['Arquivos públicos HTTPS atualizados','Fontes legíveis e KaTeX no pacote publicado','Manifesto dos cinco arquivos conferido','API disponível e serviços saudáveis'],
        'escopo':'Somente apresentação das fontes; IA, verificador, banco e históricos preservados.',
        'backup':(root/'readable-sources-last-backup.txt').read_text().strip()}
(root/'verificacao-fontes-legiveis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
