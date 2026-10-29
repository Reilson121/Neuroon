import React,{useState,useEffect} from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {requisitar,renovarCsrf} from './api.js';
import useSessaoPratica from './hooks/useSessaoPratica.js';
import Icon from './components/Icon.jsx';
import Logo from './components/Logo.jsx';
import Monitor from './components/Monitor.jsx';
import Avaliacao from './components/Avaliacao.jsx';
import Usuarios,{CamposUsuario} from './components/Usuarios.jsx';
import {Inicio,Catalogo,ContextoEstudo} from './components/StudyLayout.jsx';

const Texto=({children})=><Markdown remarkPlugins={[remarkGfm]}>{children||''}</Markdown>;
const Erro=({mensagem})=>mensagem?<p className="alert error" role="alert">{mensagem}</p>:null;
export function Fontes({fontes=[]}){
  return fontes.length?<div className="sources" aria-label="Materiais de referência">{fontes.map((f,i)=><span key={i} className="source">{f.referencia?`[${f.referencia}] `:''}{f.tituloMaterial||f.titulo_material||f.arquivo}{f.pagina?` · p. ${f.pagina}`:''}{f.paginas_mescladas?.length?`, ${f.paginas_mescladas.join(', ')}`:''}{(f.numeroQuestao||f.numero_questao)?` · questão ${f.numeroQuestao||f.numero_questao}`:''}{f.revisoes_ia?.length?' · inclui observação de IA':''}{(f.materialId||f.material_id)&&<a href={`/api/v1/materiais/${f.materialId||f.material_id}/arquivo${f.pagina?`#page=${f.pagina}`:''}`} target="_blank" rel="noopener noreferrer" aria-label={`Abrir referência ${f.referencia||i+1}`}> · Abrir fonte</a>}</span>)}</div>:null;
}
export function Grafico({dados}){
  if(!dados)return null;
  if(dados.tipo==='barras'){
    const max=Math.max(...dados.valores,1);
    return <figure><figcaption>{dados.titulo}</figcaption><svg viewBox="0 0 480 180" role="img" aria-label={dados.valores.map((v,i)=>`${dados.rotulos[i]}: ${v}`).join('; ')}>
      {dados.valores.map((v,i)=><g key={i}><rect x={25+i*430/dados.valores.length} y={145-v/max*110} width={300/dados.valores.length} height={v/max*110} rx="3"/><text x={25+i*430/dados.valores.length} y={132-v/max*110}>{v}</text><text x={25+i*430/dados.valores.length} y="167">{dados.rotulos[i]}</text></g>)}
    </svg></figure>;
  }
  if(dados.tipo==='dispersao'){
    const minX=Math.min(...dados.x),maxX=Math.max(...dados.x),minY=Math.min(...dados.y),maxY=Math.max(...dados.y);
    return <figure><figcaption>{dados.titulo} · valores exatos na tabela</figcaption><svg viewBox="0 0 480 190" role="img" aria-label={dados.x.map((v,i)=>`X ${v}, Y ${dados.y[i]}`).join('; ')}>
      <path d="M40 15V160H455" fill="none" stroke="currentColor"/>{dados.x.map((v,i)=><g key={i}><circle cx={60+(v-minX)/(maxX-minX||1)*370} cy={140-(dados.y[i]-minY)/(maxY-minY||1)*110} r="5"/><text x={60+(v-minX)/(maxX-minX||1)*370} y="180">{v}</text></g>)}<text x="8" y="25">Y</text><text x="460" y="180">X</text>
    </svg></figure>;
  }
  return null;
}
export function Correcao({dados}){
 return <section className={`feedback ${dados.correto?'success':'review'}`} aria-live="polite">
  <h3>{dados.correto?'Você acertou.':'Vamos entender esta questão.'}</h3><p><strong>Alternativa correta: {dados.alternativaCorreta}</strong></p>
  <p><strong>Conceito:</strong> {dados.conceito}</p>
  {dados.formula&&<><h4>Fórmula</h4><p className="formula">{dados.formula}</p></>}
  {dados.substituicao&&<><h4>Substituição dos valores</h4><p>{dados.substituicao}</p></>}
  {!!dados.calculos?.length&&<><h4>Resolução passo a passo</h4><ol>{dados.calculos.map((p,i)=><li key={i}>{p}</li>)}</ol></>}
  <h4>Resolução</h4><Texto>{dados.resolucao}</Texto>
  {!!dados.errosComuns?.length&&<><h4>Erros comuns</h4><ul>{dados.errosComuns.map((p,i)=><li key={i}>{p}</li>)}</ul></>}
  <p className="tip"><strong>Para a próxima:</strong> {dados.dica}</p>
  {dados.aviso&&<p className="notice">{dados.aviso}</p>}<Fontes fontes={dados.fontes}/>
 </section>;
}
export function Questao({questao,sessaoId,indice,total}){
 const [alternativa,setAlternativa]=useState(''),[correcao,setCorrecao]=useState(null),[busy,setBusy]=useState(false),[erro,setErro]=useState('');
 async function responder(e){e.preventDefault();setBusy(true);setErro('');try{setCorrecao(await requisitar(`/api/v1/pratica/sessoes/${sessaoId}/respostas`,{method:'POST',body:{questaoId:questao.id,alternativa}}));}catch(e){setErro(e.message);}finally{setBusy(false);}}
 return <article className="question card"><div className="eyebrow">Questão {indice+1} de {total} <span className="badge">{questao.origem==='GERADA_IA'?'Inédita · IA':'Material acadêmico'}</span></div>
  <Texto>{questao.enunciado}</Texto><Grafico dados={questao.visualizacao}/>
  {questao.aviso&&<p className="notice">{questao.aviso}</p>}
  <form onSubmit={responder}><fieldset disabled={busy||!!correcao}><legend className="sr-only">Escolha uma alternativa</legend>
   {Object.entries(questao.alternativas).map(([letra,texto])=><label className={`option ${alternativa===letra?'selected':''}`} key={letra}><input type="radio" name={questao.id} value={letra} checked={alternativa===letra} onChange={()=>setAlternativa(letra)}/><span className="letter">{letra}</span><span>{texto}</span></label>)}
  </fieldset><Erro mensagem={erro}/>{!correcao&&<button disabled={!alternativa||busy}>{busy?'Conferindo…':'Conferir resposta'}</button>}</form>
  <Fontes fontes={questao.fontes}/>{correcao&&<Correcao dados={correcao}/>}
 </article>;
}
export function Pratica({disciplina,assuntoId}){
 const digitais=disciplina.nome==='Sistemas Digitais';
 const [modo,setModo]=useState(digitais?'GERADAS_IA':'CADASTRADAS'),[origem,setOrigem]=useState('MISTO'),[quantidade,setQuantidade]=useState(5);
 useEffect(()=>{setModo(digitais?'GERADAS_IA':'CADASTRADAS');setOrigem('MISTO');},[digitais]);
 const {sessao,busy,erro,iniciar}=useSessaoPratica({disciplinaId:disciplina.id,assuntoId,habilitada:disciplina.possuiProva,modo,origem,quantidade});
 if(!disciplina.possuiProva)return <div className="empty card"><h3>Prática ainda não habilitada</h3><p>Esta disciplina não está disponível para prática com questões.</p></div>;
 return <><div className="card practice-controls"><div><h2>Aprenda resolvendo</h2><p>Escolha o tipo de prática. A correção explica o caminho até a resposta.</p></div>
 <div className="controls"><label>Questões<select value={modo} disabled={busy} onChange={e=>setModo(e.target.value)}><option value="CADASTRADAS">Dos materiais acadêmicos</option><option value="GERADAS_IA">Inéditas geradas por IA</option></select></label>
 <label>Referência<select value={origem} disabled={busy} onChange={e=>setOrigem(e.target.value)}><option value="MISTO">{digitais&&modo==='GERADAS_IA'?'Materiais teóricos disponíveis':'Listas e provas'}</option><option value="LISTA">Listas</option><option value="PROVA">Provas anteriores</option></select></label>
 <label>Quantidade<select value={quantidade} disabled={busy} onChange={e=>setQuantidade(Number(e.target.value))}>{[1,3,5,10].map(n=><option key={n}>{n}</option>)}</select></label>
 <button onClick={()=>iniciar()} disabled={busy}>{busy?'Preparando e conferindo…':sessao?'Nova prática':'Iniciar prática'}</button></div>
 <p className="notice">{modo==='GERADAS_IA'?'Os conceitos seguem os materiais autorizados. Os cálculos são conferidos antes da exibição. Questões de IA não são provas oficiais.':'As questões preservam a origem. Resoluções de IA são identificadas; a autoria oficial do gabarito da lista ainda não foi confirmada.'}</p></div>
 {digitais&&<p className="notice">A lista e a prova do professor ainda não foram fornecidas. Pratique com questões conceituais e contextualizadas criadas por IA a partir dos PDFs disponíveis. A quantidade pode ser menor em assuntos com poucas questões; use a revisão para refazê-las.</p>}
 <Erro mensagem={erro}/>{busy&&<p role="status">Aguarde enquanto preparamos sua prática…</p>}
 {sessao?.estado==='SEM_QUESTOES'&&<div className="card empty" role="status"><span className="empty-mark">○</span><h3>Nenhuma questão disponível nesta seleção</h3><p>{sessao.mensagem}</p><p>Selecione outro assunto ou modo de prática.</p><button className="secondary" disabled={busy} onClick={()=>iniciar(true)}>Revisar questões já vistas</button></div>}
 {sessao?.questoes.map((q,i)=><Questao key={`${sessao.sessaoId}-${q.id}`} questao={q} sessaoId={sessao.sessaoId} indice={i} total={sessao.questoes.length}/>)}</>;
}
export function Materiais({materiais,usuario,onUpdate}){
 const [erro,setErro]=useState(''),[busy,setBusy]=useState(null);
 async function alterar(m){setBusy(m.id);setErro('');try{await requisitar(`/api/v1/admin/materiais/${m.id}`,{method:'PUT',body:{ativo:true,fonteMonitorVirtual:m.fonteMonitorVirtual,disponivelParaPratica:!m.disponivelParaPratica,autorizacaoProfessor:m.autorizacaoProfessor}});await onUpdate();}catch(e){setErro(e.message);}finally{setBusy(null);}}
 return <div className="card materials-card"><div className="card-heading"><span className="feature-icon blue"><Icon name="folder"/></span><div><h2>Materiais da disciplina</h2><p>Suas referências para entender e praticar.</p></div></div><Erro mensagem={erro}/>{!materiais.length&&<div className="empty"><Icon name="folder" size={32}/><h3>Nenhum material disponível</h3><p>Os materiais aparecerão aqui quando forem disponibilizados.</p></div>}{materiais.map(m=><article className="material" key={m.id}><span className="file-icon"><Icon name="book"/></span><div className="material-info"><span className="eyebrow">{m.tipo.replaceAll('_',' ')}</span><h3>{m.titulo}</h3><p>{m.fonteMonitorVirtual?'Fonte do Monitor Virtual':m.disponivelParaPratica?'Referência autorizada para prática':'Prática indisponível'}</p>{m.contemGabarito&&<small>Contém gabarito · autoria oficial não confirmada</small>}</div>{m.arquivoDisponivel&&<a className="secondary" href={`/api/v1/materiais/${m.id}/arquivo`} target="_blank" rel="noopener noreferrer" aria-label={`Abrir ${m.titulo}`}>Abrir material</a>}{usuario.perfil==='ADMINISTRADOR'&&m.tipo!=='SLIDE_AULA'&&<button disabled={busy!==null||!m.autorizacaoProfessor} className="secondary" onClick={()=>alterar(m)}>{busy===m.id?'Atualizando…':m.disponivelParaPratica?'Suspender prática':'Habilitar prática'}</button>}</article>)}</div>;
}
export function Login({onLogin}){
 const [cadastro,setCadastro]=useState(false),[dados,setDados]=useState({nome:'',email:'',senha:''}),[aviso,setAviso]=useState('');
 async function cadastrar(e){e.preventDefault();setBusy(true);setErro('');try{await requisitar('/api/v1/auth/cadastro',{method:'POST',body:dados});setEmail(dados.email);setDados({nome:'',email:'',senha:''});setCadastro(false);setAviso('Conta criada! Entre com seu email e senha.');}catch(e){setErro(e.message);}finally{setBusy(false);}}
 const [email,setEmail]=useState(''),[senha,setSenha]=useState(''),[busy,setBusy]=useState(false),[erro,setErro]=useState('');
 async function entrar(e){e.preventDefault();setBusy(true);setErro('');try{const user=await requisitar('/api/v1/auth/login',{method:'POST',body:{email,senha}});setSenha('');await renovarCsrf();onLogin(user);}catch(e){setErro(e.message);}finally{setBusy(false);}}
 async function entrarVisitante(){setBusy(true);setErro('');try{const user=await requisitar('/api/v1/auth/visitante',{method:'POST'});await renovarCsrf();onLogin(user);}catch(e){setErro(e.message);}finally{setBusy(false);}}
 return <main className="login"><section className="login-intro"><div className="login-brand"><Logo/></div><div className="login-copy"><span className="eyebrow">Conhecimento que conecta</span><h1>Aprender fica melhor<br/>quando a gente<br/><em>conecta ideias.</em></h1><p>Seu espaço para tirar dúvidas, explorar materiais e praticar no seu ritmo.</p><div className="login-features"><span><Icon name="spark"/> Monitor Virtual com IA</span><span><Icon name="practice"/> Prática com explicações</span><span><Icon name="history"/> Suas conversas, sempre por perto</span></div></div><p className="login-footer">NEURON · Aprenda. Conecte. Evolua.</p></section><section className="login-side"><form className="card login-form" onSubmit={cadastro?cadastrar:entrar}><span className="feature-icon blue"><Icon name="user" size={24}/></span><h2>{cadastro?'Crie sua conta':'Bom ter você aqui!'}</h2><p>{cadastro?'Cadastre-se para começar a aprender.':'Entre na sua conta e continue aprendendo.'}</p>{aviso&&<p role="status">{aviso}</p>}{cadastro?<CamposUsuario dados={dados} setDados={setDados} disabled={busy}/>:<><label>Email<input type="email" autoComplete="username" placeholder="Seu email" required value={email} onChange={e=>setEmail(e.target.value)} maxLength="255"/></label><label>Senha<input type="password" autoComplete="current-password" placeholder="Sua senha" required value={senha} onChange={e=>setSenha(e.target.value)} maxLength="200"/></label></>}<Erro mensagem={erro}/><button disabled={busy}>{busy?'Aguarde…':cadastro?'Criar conta':'Entrar'}<Icon name="arrow" size={17}/></button><button type="button" className="secondary" disabled={busy} onClick={()=>{setCadastro(!cadastro);setErro('');setAviso('');setSenha('');setDados({nome:'',email:'',senha:''});}}>{cadastro?'Já tenho conta':'Criar uma conta'}</button><button type="button" className="secondary" disabled={busy} onClick={entrarVisitante}>Explorar sem conta</button><small>Como visitante, você pode explorar materiais e usar o Monitor. Seu histórico é temporário.</small></form></section></main>;
}
const paginas=[{id:'usuarios',label:'Usuários',icon:'user',admin:true},{id:'inicio',label:'Início',icon:'home'},{id:'disciplinas',label:'Disciplinas',icon:'book'},{id:'monitor',label:'Monitor Virtual',icon:'spark'},{id:'pratica',label:'Praticar',icon:'practice'},{id:'materiais',label:'Materiais',icon:'folder'},{id:'avaliacao',label:'Avaliar plataforma',icon:'star',estudante:true}];
export default function App(){
 const [usuario,setUsuario]=useState(null),[carregando,setCarregando]=useState(true),[periodos,setPeriodos]=useState([]),[periodo,setPeriodo]=useState(''),[disciplinas,setDisciplinas]=useState([]),[disciplinaId,setDisciplinaId]=useState(''),[assuntos,setAssuntos]=useState([]),[assuntoId,setAssuntoId]=useState(null),[materiais,setMateriais]=useState([]),[pagina,setPagina]=useState('inicio'),[erro,setErro]=useState(''),[catalogoBusy,setCatalogoBusy]=useState(false);
 useEffect(()=>{requisitar('/api/v1/auth/me').then(setUsuario).catch(()=>{}).finally(()=>setCarregando(false));},[]);
 useEffect(()=>{document.scrollingElement?.scrollTo?.({top:0});},[pagina]);
 useEffect(()=>{let active=true;if(usuario){setErro('');requisitar('/api/v1/periodos').then(ps=>{if(active){setPeriodos(ps);setPeriodo(ps.find(p=>p.numero===3)?.id||ps[0]?.id||'');}}).catch(e=>{if(active)setErro(e.message);});}return()=>{active=false;};},[usuario]);
 useEffect(()=>{setDisciplinaId('');setDisciplinas([]);setAssuntoId(null);setAssuntos([]);setMateriais([]);if(periodo&&usuario){let active=true;setCatalogoBusy(true);setErro('');requisitar(`/api/v1/periodos/${periodo}/disciplinas`).then(ds=>{if(active){setDisciplinas(ds);setDisciplinaId(ds[0]?.id||'');}}).catch(e=>{if(active)setErro(e.message);}).finally(()=>{if(active)setCatalogoBusy(false);});return()=>{active=false;};}},[periodo,usuario]);
 useEffect(()=>{setAssuntoId(null);setAssuntos([]);setMateriais([]);if(disciplinaId&&usuario){let active=true;setCatalogoBusy(true);setErro('');Promise.all([requisitar(`/api/v1/disciplinas/${disciplinaId}/assuntos`),requisitar(`/api/v1/disciplinas/${disciplinaId}/materiais`)]).then(([a,m])=>{if(active){setAssuntos(a);setMateriais(m);}}).catch(e=>{if(active)setErro(e.message);}).finally(()=>{if(active)setCatalogoBusy(false);});return()=>{active=false;};}},[disciplinaId,usuario]);
 const disciplina=disciplinas.find(d=>d.id===Number(disciplinaId));
 const assuntoNome=assuntos.find(a=>a.id===assuntoId)?.nome;
 const periodoNome=periodos.find(p=>p.id===Number(periodo))?.nome;
 const iniciais=usuario?.nome?.split(' ').filter(Boolean).slice(0,2).map(n=>n[0]).join('')||'EU';
 const navegacao=paginas.filter(p=>(!p.admin||usuario?.perfil==='ADMINISTRADOR')&&(!p.estudante||usuario?.perfil==='ESTUDANTE')&&(usuario?.perfil!=='VISITANTE'||p.id!=='pratica'));
 async function sair(){try{await requisitar('/api/v1/auth/logout',{method:'POST'});setUsuario(null);setPeriodo('');setPagina('inicio');setErro('');await renovarCsrf();}catch(e){setErro(e.message);}}
 function selecionarDisciplina(id){setAssuntoId(null);setDisciplinaId(id);setPagina('monitor');}
 if(carregando)return <main className="loading" role="status"><Logo/><span className="loading-dot"/>Abrindo seu espaço de estudo…</main>;
 if(!usuario)return <Login onLogin={u=>{setPagina('inicio');setUsuario(u);}}/>;
 return <div className="app"><a className="skip-link" href="#conteudo">Pular para o conteúdo</a><aside className="sidebar"><button className="sidebar-logo" aria-label="NEURON — ir para o início" onClick={()=>setPagina('inicio')}><Logo/></button><span className="sidebar-caption">SEU ESPAÇO DE APRENDIZADO</span><nav aria-label="Navegação principal">{navegacao.map(p=><button key={p.id} className={pagina===p.id?'active':''} aria-current={pagina===p.id?'page':undefined} onClick={()=>setPagina(p.id)}><Icon name={p.icon} size={19}/><span>{p.label}</span>{pagina===p.id&&<span className="nav-indicator"/>}</button>)}</nav><div className="sidebar-tip"><span className="sidebar-tip-icon"><Icon name="spark" size={21}/></span><strong>Uma dúvida é um bom começo.</strong><p>Explore, pergunte e aprenda no seu ritmo.</p></div><div className="sidebar-user"><span className="avatar">{iniciais}</span><div><strong>{usuario.nome}</strong><small>{usuario.perfil==='ADMINISTRADOR'?'Administrador':usuario.perfil==='VISITANTE'?'Visitante':'Estudante'}</small></div><button className="icon-button" onClick={sair} aria-label="Sair da conta"><Icon name="logout" size={18}/></button></div></aside>
 <div className="main-layout"><header className="topbar"><span className="topbar-title">{paginas.find(p=>p.id===pagina)?.label}</span><span className="top-caption">Aprenda. Conecte. Evolua.</span><div className="topbar-user"><span className="avatar small">{iniciais}</span><span>{usuario.nome.split(' ')[0]}</span><button className="icon-button mobile-logout" onClick={sair} aria-label="Sair da conta"><Icon name="logout" size={18}/></button></div><button className="mobile-brand" onClick={()=>setPagina('inicio')} aria-label="NEURON — ir para o início"><Logo/></button></header>
 <main id="conteudo" className={`workspace page-${pagina}`}><Erro mensagem={erro}/>{pagina==='usuarios'&&usuario.perfil==='ADMINISTRADOR'?<Usuarios/>:pagina==='inicio'?<Inicio usuario={usuario} disciplina={disciplina} periodoNome={periodoNome} quantidadeDisciplinas={disciplinas.length} quantidadeMateriais={materiais.length} nav={setPagina}/>:pagina==='avaliacao'?<Avaliacao key={usuario.id}/>:pagina==='disciplinas'?<Catalogo usuario={usuario} periodos={periodos} periodo={periodo} setPeriodo={setPeriodo} disciplinas={disciplinas} busy={catalogoBusy} selecionar={selecionarDisciplina}/>:<><div className="page-title"><span className="eyebrow">{periodoNome||'Seu espaço de estudo'}</span><h1>{pagina==='monitor'?'Vamos tirar suas dúvidas?':pagina==='pratica'?'Aprenda na prática':'Sua biblioteca de estudo'}</h1><p>{pagina==='monitor'?'Converse com o Monitor Virtual e retome suas explicações quando precisar.':pagina==='pratica'?'Transforme o que você estudou em conhecimento.':'Encontre os materiais que acompanham sua jornada.'}</p></div><ContextoEstudo periodos={periodos} periodo={periodo} setPeriodo={setPeriodo} disciplinas={disciplinas} disciplinaId={disciplinaId} setDisciplinaId={setDisciplinaId} assuntos={assuntos} assuntoId={assuntoId} setAssuntoId={setAssuntoId} busy={catalogoBusy}/>{catalogoBusy?<div className="card empty" role="status"><span className="loading-dot"/><p>Preparando sua disciplina…</p></div>:disciplina?<section key={`${usuario.id}-${disciplina.id}-${assuntoId}-${pagina}`}>{pagina==='monitor'?<Monitor disciplina={disciplina} assuntoId={assuntoId} assuntoNome={assuntoNome} Fontes={Fontes}/>:pagina==='pratica'?<Pratica disciplina={disciplina} assuntoId={assuntoId}/>:<Materiais materiais={materiais.filter(m=>!assuntoId||!m.assuntoId||m.assuntoId===assuntoId)} usuario={usuario} onUpdate={async()=>setMateriais(await requisitar(`/api/v1/disciplinas/${disciplina.id}/materiais`))}/>}</section>:<div className="card empty"><Icon name="book" size={34}/><h2>Escolha uma disciplina para começar</h2><p>Selecione um período com disciplinas disponíveis.</p></div>}</>}</main><footer className="app-footer">NEURON <span>Conhecimento que conecta.</span></footer></div><nav className="mobile-nav" aria-label="Navegação no celular">{navegacao.map(p=><button key={p.id} className={pagina===p.id?'active':''} aria-current={pagina===p.id?'page':undefined} onClick={()=>setPagina(p.id)}><Icon name={p.icon} size={21}/><span>{p.id==='avaliacao'?'Avaliar':p.label==='Monitor Virtual'?'Monitor IA':p.label}</span></button>)}</nav></div>;
}
