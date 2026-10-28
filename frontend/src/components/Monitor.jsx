import React,{useEffect,useRef,useState} from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {requisitar,conversar} from '../api.js';
import Icon from './Icon.jsx';

const horario=data=>data?new Date(data).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}):'';
const dia=data=>new Date(data).toLocaleDateString('pt-BR',{day:'2-digit',month:'short'});

export default function Monitor({disciplina,assuntoId,assuntoNome,Fontes}){
 const [conversas,setConversas]=useState([]),[threadId,setThreadId]=useState(null),[mensagens,setMensagens]=useState([]),[pergunta,setPergunta]=useState('');
 const [busy,setBusy]=useState(false),[loading,setLoading]=useState(true),[erro,setErro]=useState(''),[status,setStatus]=useState(''),[historyOpen,setHistoryOpen]=useState(false);
 const controller=useRef(null),historicoController=useRef(null),contentRef=useRef(null),inputRef=useRef(null),sequence=useRef(0);
 const listaUrl=`/api/v1/monitor/conversas?disciplinaId=${disciplina.id}${assuntoId?`&assuntoId=${assuntoId}`:''}`;

 useEffect(()=>{
  setLoading(true);setThreadId(null);setMensagens([]);setPergunta('');setErro('');setBusy(false);
  const abort=new AbortController();historicoController.current=abort;
  requisitar(listaUrl,{signal:abort.signal}).then(dados=>{if(!abort.signal.aborted)setConversas(dados);}).catch(e=>{if(!abort.signal.aborted&&e.name!=='AbortError')setErro('Não foi possível carregar seu histórico. Tente novamente.');}).finally(()=>{if(!abort.signal.aborted)setLoading(false);});
  return()=>{sequence.current++;abort.abort();controller.current?.abort();historicoController.current?.abort();};
 },[listaUrl]);
 useEffect(()=>{if(mensagens.length||busy){const area=contentRef.current;area?.scrollTo?.({top:area.scrollHeight,behavior:'smooth'});}},[mensagens,busy]);

 async function abrir(id){
  if(busy)return;
  const seq=++sequence.current;historicoController.current?.abort();const abort=new AbortController();historicoController.current=abort;
  setLoading(true);setErro('');
  try{const detalhe=await requisitar(`/api/v1/monitor/conversas/${id}`,{signal:abort.signal});if(seq!==sequence.current)return;setThreadId(detalhe.conversa.id);setMensagens(detalhe.mensagens);setPergunta('');setHistoryOpen(false);}
  catch(e){if(seq===sequence.current&&e.name!=='AbortError')setErro(e.message);}
  finally{if(seq===sequence.current)setLoading(false);}
 }
 function nova(){if(busy)return;sequence.current++;historicoController.current?.abort();setLoading(false);setThreadId(null);setMensagens([]);setPergunta('');setErro('');setHistoryOpen(false);inputRef.current?.focus();}
 async function atualizarHistorico(){
  try{const dados=await requisitar(listaUrl,{signal:controller.current?.signal});setConversas(dados);}
  catch(e){if(e.name!=='AbortError')setErro('A resposta foi salva, mas a lista de conversas não atualizou. Reabra o Monitor para carregá-la.');}
 }
 async function enviar(e){
  e.preventDefault();const texto=pergunta.trim();if(!texto||busy||loading)return;
  const seq=++sequence.current,localId=`envio-${seq}`;let concluida=false;
  const abort=new AbortController();controller.current=abort;
  setBusy(true);setErro('');setStatus('Consultando os materiais da disciplina…');setPergunta('');
  setMensagens(p=>[...p,{id:`${localId}-user`,papel:'USUARIO',conteudo:texto,criadoEm:new Date().toISOString(),fontes:[]},{id:localId,papel:'MONITOR',conteudo:'',fontes:[],criadoEm:new Date().toISOString()}]);
  try{
   await conversar({disciplinaId:disciplina.id,assuntoId:assuntoId||null,pergunta:texto,threadId},(event,data)=>{
    if(seq!==sequence.current)return;
    if(event==='status')setStatus(data.mensagem);
    if(event==='token')setMensagens(p=>p.map(m=>m.id===localId?{...m,conteudo:m.conteudo+data.texto}:m));
    if(event==='sources')setMensagens(p=>p.map(m=>m.id===localId?{...m,fontes:data.fontes||[]}:m));
    if(event==='done'){concluida=true;setThreadId(data.threadId);setStatus('');}
    if(event==='error')throw new Error(data.mensagem);
   },abort.signal);
   if(!concluida)throw new Error('Não foi possível confirmar o salvamento da resposta. Reabra o histórico antes de tentar novamente.');
   await atualizarHistorico();
  }catch(e){
   if(e.name!=='AbortError'&&seq===sequence.current){setErro(e.message);if(!concluida){setMensagens(p=>p.filter(m=>m.id!==localId&&m.id!==`${localId}-user`));setPergunta(texto);}}
  }finally{if(seq===sequence.current){setBusy(false);setStatus('');inputRef.current?.focus();}}
 }
 const titulo=conversas.find(c=>c.id===threadId)?.titulo||'Nova conversa';
 return <div className={`monitor-layout ${historyOpen?'history-open':''}`} onKeyDown={e=>{if(e.key==='Escape')setHistoryOpen(false);}}>
  <aside className="chat-history" aria-label="Histórico do Monitor Virtual">
   <div className="history-heading"><div><span className="eyebrow">Seu espaço de estudo</span><h3>Conversas</h3></div><button className="icon-button history-close" onClick={()=>setHistoryOpen(false)} aria-label="Fechar histórico"><Icon name="close"/></button></div>
   <button className="new-chat" onClick={nova} disabled={busy}><Icon name="plus" size={17}/> Nova conversa</button>
   <p className="history-context">{assuntoNome||disciplina.nome}</p>
   <div className="history-list">{!loading&&!conversas.length&&<p className="history-empty">Suas conversas aparecerão aqui após a primeira resposta.</p>}{conversas.map(c=><button key={c.id} className={`history-item ${threadId===c.id?'active':''}`} onClick={()=>abrir(c.id)} disabled={busy||loading}><Icon name="chat" size={16}/><span><strong>{c.titulo}</strong><small>{dia(c.atualizadoEm)}</small></span></button>)}</div>
   <div className="history-note"><Icon name="shield" size={16}/><span>Histórico salvo na sua conta.</span></div>
  </aside>
  <section className="chat-panel" aria-label="Conversa com o Monitor Virtual">
   <header className="chat-header"><span className="monitor-avatar"><Icon name="spark" size={22}/></span><div><h2>Monitor Virtual</h2><p>{assuntoNome||disciplina.nome}</p></div><span className="grounded-label"><span/> Apoiado nos materiais</span><button className="icon-button history-toggle" aria-label="Abrir histórico" onClick={()=>setHistoryOpen(true)}><Icon name="history"/></button></header>
   <div ref={contentRef} className="chat-content" aria-live="polite" aria-busy={busy||loading}>
    {loading?<div className="chat-welcome"><span className="loading-dot"/><p>Carregando suas conversas…</p></div>:!mensagens.length?<div className="chat-welcome"><span className="welcome-spark"><Icon name="spark" size={34}/></span><span className="eyebrow">Vamos aprender juntos</span><h3>Qual é a sua dúvida?</h3><p>Pergunte sobre {assuntoNome||disciplina.nome}. Vou buscar a explicação nos materiais da disciplina.</p><div className="suggestions">{['Explique os principais conceitos deste assunto.','Como aplicar esse conteúdo em um exercício?'].map(texto=><button key={texto} onClick={()=>{setPergunta(texto);inputRef.current?.focus();}}>{texto}<Icon name="arrow" size={14}/></button>)}</div></div>:<><div className="conversation-title"><span>{titulo}</span></div>{mensagens.map(m=><article key={m.id} className={`chat-message ${m.papel==='USUARIO'?'from-user':'from-monitor'}`} aria-label={m.papel==='USUARIO'?'Sua mensagem':'Resposta do Monitor'}>{m.papel==='MONITOR'&&<span className="message-avatar"><Icon name="spark" size={17}/></span>}<div className="message-body"><div className="message-bubble">{m.conteudo?<Markdown remarkPlugins={[remarkGfm]}>{m.conteudo}</Markdown>:<div className="typing-indicator" aria-label="Preparando resposta"><i/><i/><i/></div>}{m.fontes?.length>0&&<details className="message-sources"><summary><Icon name="book" size={13}/> {m.fontes.length} {m.fontes.length===1?'fonte consultada':'fontes consultadas'}<Icon name="chevron" size={13}/></summary><Fontes fontes={m.fontes}/></details>}</div><span className="message-time">{m.papel==='USUARIO'?'Você':'Monitor Virtual'} · {horario(m.criadoEm)}</span></div></article>)}</>}
    {busy&&<p className="chat-status" role="status">{status}</p>}
   </div>
   <div className="composer-area">{erro&&<p className="alert error" role="alert">{erro}</p>}<form className="chat-composer" onSubmit={enviar}><label className="sr-only" htmlFor="pergunta">Sua pergunta ao Monitor Virtual</label><textarea id="pergunta" ref={inputRef} value={pergunta} onChange={e=>setPergunta(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();enviar(e);}}} rows="1" maxLength="4000" placeholder="Digite sua dúvida aqui…" disabled={busy||loading}/><button type="submit" aria-label="Enviar pergunta" disabled={!pergunta.trim()||busy||loading}><Icon name="send" size={19}/></button></form><div className="composer-note"><span>Confira as fontes. A IA pode cometer erros.</span><span>{pergunta.length}/4000</span></div></div>
  </section>
 </div>;
}
