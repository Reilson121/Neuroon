import json,re,subprocess,urllib.request,urllib.error,hashlib
from pathlib import Path
R=Path('/opt/neuron');base='https://neuron-45-159-173-74.sslip.io'
def fetch(p):
 with urllib.request.urlopen(base+p,timeout=45) as r:
  assert r.status==200
  return r.read().decode()
data=json.loads(fetch('/api/v1/avaliacoes'))
assert data['total']>=2 and len(data['avaliacoes'])>0
assert all(set(a)=={'id','aluno','nota','comentario','enviadoEm'} and 1<=a['nota']<=5 for a in data['avaliacoes'])
for path in ['/api/v1/avaliacao-plataforma/minha','/api/v1/admin/usuarios']:
 try:fetch(path);raise AssertionError('Rota privada ficou pública')
 except urllib.error.HTTPError as e:assert e.code==401
html=fetch('/');js_path=re.search(r'src="(/assets/[^\"]+\.js)"',html).group(1);js=fetch(js_path)
assert all(s in js for s in ['Ver avaliações dos alunos','Avaliações dos alunos','/api/v1/avaliacoes?pagina=','Sua avaliação é pública:'])
assert 'Seu comentário não é exibido para outros alunos.' not in js
manifest=json.loads((R/'avaliacoes-manifest.json').read_text())
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==e['sha256'] for n,e in manifest.items())
states=subprocess.run(['docker','compose','--env-file','deploy/.env','-f','deploy/compose.yaml','ps','--format','{{.Service}} {{.State}} {{.Health}}'],cwd=R,text=True,capture_output=True,check=True).stdout
assert all(s+' running healthy' in states for s in ['backend','db','ai'])
report={'aprovado':True,'total_avaliacoes':data['total'],'media':data['media'],'verificacoes':['Consulta pública sem login','Campos públicos sem email ou senha','Rotas privadas continuam protegidas','Interface atualizada e aviso de publicação','Arquivos publicados conferidos e serviços saudáveis'],'backup':(R/'avaliacoes-last-backup.txt').read_text().strip()}
(R/'verificacao-avaliacoes-publicadas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
