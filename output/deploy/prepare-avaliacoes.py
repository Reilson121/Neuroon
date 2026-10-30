import hashlib,json,subprocess,tarfile
from pathlib import Path
R=Path(__file__).resolve().parents[2]; O=R/'output/deploy'
files=['frontend/src/App.jsx','frontend/src/components/Avaliacao.jsx','frontend/src/components/Avaliacoes.jsx','frontend/src/components/Avaliacoes.css','backend/demo/src/main/java/com/Neuron/demo/avaliacao/AvaliacoesController.java','backend/demo/src/main/java/com/Neuron/demo/avaliacao/AvaliacaoPlataformaRepository.java','backend/demo/src/main/java/com/Neuron/demo/security/SecurityConfig.java']
ssh=['ssh','-i','deploy/access/neuron_enuvem','-o','UserKnownHostsFile=deploy/access/known_hosts','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','root@45.159.173.74']
code="import json,hashlib;from pathlib import Path;r=Path('/opt/neuron');print(json.dumps({n:dict(text=(r/n).read_text(),sha256=hashlib.sha256((r/n).read_bytes()).hexdigest()) if (r/n).exists() else None for n in "+repr(files)+"}))"
r=subprocess.run([*ssh,'python3 -'],input=code,text=True,encoding='utf-8',capture_output=True,cwd=R,check=True);remote=json.loads(r.stdout)
def replace(s,old,new):
 if s.count(old)!=1:raise ValueError('Contexto divergente: '+old[:75])
 return s.replace(old,new,1)
stage=O/'avaliacoes-stage';manifest={}
for n in files:
 s=(R/n).read_text(encoding='utf-8')
 if n.endswith('App.jsx'):
  s=remote[n]['text'];s=replace(s,"import Avaliacao from './components/Avaliacao.jsx';","import Avaliacao from './components/Avaliacao.jsx';\nimport Avaliacoes from './components/Avaliacoes.jsx';")
  s=replace(s,"{id:'avaliacao',label:'Avaliar plataforma'","{id:'avaliacoes',label:'Avaliações',icon:'star'},{id:'avaliacao',label:'Avaliar plataforma'")
  s=replace(s,"pagina==='usuarios'&&usuario.perfil==='ADMINISTRADOR'?<Usuarios/>","pagina==='avaliacoes'?<Avaliacoes/>:pagina==='usuarios'&&usuario.perfil==='ADMINISTRADOR'?<Usuarios/>")
  local=(R/n).read_text(encoding='utf-8');extra=local.split('export default function App(){',1)[1].split(' const [usuario',1)[0]
  s=replace(s,'export default function App(){','export default function App(){'+extra.rstrip('\n'))
  s=replace(s,' if(carregando)return',' if(avaliacoesPublicas)return <main className="public-reviews"><a className="secondary" href="#">Voltar à plataforma</a><Avaliacoes/></main>;\n if(carregando)return')
  s=replace(s,"{import.meta.env.VITE_GUEST_ENABLED!=='false'&&",'<a className="secondary" href="#avaliacoes">Ver avaliações dos alunos</a>{import.meta.env.VITE_GUEST_ENABLED!==\'false\'&&')
 elif remote[n]:
  # Existing files must match the local baseline, allowing only these feature changes.
  old=remote[n]['text']
  if n.endswith('Avaliacao.jsx'):
   old=replace(old,'A avaliação fica vinculada à sua conta. Seu comentário não é exibido para outros alunos.','Sua avaliação é pública: seu nome, nota, comentário e data ficam visíveis na página de avaliações.')
  elif n.endswith('SecurityConfig.java'):
   old=replace(old,'.requestMatchers("/api/v1/admin/**")','.requestMatchers(org.springframework.http.HttpMethod.GET,"/api/v1/avaliacoes").permitAll()\n    .requestMatchers("/api/v1/admin/**")')
  elif n.endswith('AvaliacaoPlataformaRepository.java'):
   old=replace(old,'import java.util.Optional;','import java.util.Optional;\nimport org.springframework.data.domain.Page;\nimport org.springframework.data.domain.Pageable;\nimport org.springframework.data.jpa.repository.EntityGraph;\nimport org.springframework.data.jpa.repository.Query;')
   extra=s.split(' @EntityGraph',1)[1].rsplit('}',1)[0]
   old=replace(old,'\n}', '\n @EntityGraph'+extra+'}')
  if old.strip()!=s.strip():raise ValueError('Arquivo remoto diverge: '+n)
 p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
 manifest[n]={'expected':remote[n]['sha256'] if remote[n] else None,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
mp=O/'avaliacoes-manifest.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with tarfile.open(O/'avaliacoes-update.tar.gz','w:gz') as t:
 for n in files:t.add(stage/n,arcname=n,recursive=False)
 t.add(mp,arcname='avaliacoes-manifest.json')
print('PACOTE_PREPARADO',len(files))
