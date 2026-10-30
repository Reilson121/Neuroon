import React,{useEffect,useRef,useState} from 'react';
import {requisitar} from '../api.js';
import Icon from './Icon.jsx';

const notas=['','Muito ruim','Ruim','Regular','Boa','Excelente'];

export default function Avaliacao(){
 const [nota,setNota]=useState(0),[comentario,setComentario]=useState(''),[atual,setAtual]=useState(null);
 const [loading,setLoading]=useState(true),[busy,setBusy]=useState(false),[erro,setErro]=useState(''),[sucesso,setSucesso]=useState(false);
 const [falhaCarga,setFalhaCarga]=useState(false),[tentativa,setTentativa]=useState(0);
 const envio=useRef(null),mensagemRef=useRef(null);
 useEffect(()=>{
  setLoading(true);setErro('');setFalhaCarga(false);
  const controller=new AbortController();
  requisitar('/api/v1/avaliacao-plataforma/minha',{signal:controller.signal}).then(dados=>{
   if(controller.signal.aborted)return;
   setAtual(dados);setNota(dados?.nota||0);setComentario(dados?.comentario||'');
  }).catch(e=>{if(!controller.signal.aborted&&e.name!=='AbortError'){setFalhaCarga(true);setErro('Não foi possível carregar sua avaliação. Tente novamente.');}}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  return()=>{controller.abort();envio.current?.abort();};
 },[tentativa]);
 async function salvar(e){
  e.preventDefault();if(busy||!nota||loading)return;
  const controller=new AbortController();envio.current=controller;setBusy(true);setErro('');setSucesso(false);
  try{const dados=await requisitar('/api/v1/avaliacao-plataforma/minha',{method:'PUT',body:{nota,comentario:comentario.trim()},signal:controller.signal});if(controller.signal.aborted)return;setAtual(dados);setNota(dados.nota);setComentario(dados.comentario||'');setSucesso(true);}
  catch(e){if(e.name!=='AbortError')setErro(e.message);}
  finally{if(!controller.signal.aborted)setBusy(false);}
 }
 useEffect(()=>{if(sucesso)mensagemRef.current?.focus();},[sucesso]);
 const alterada=!atual||nota!==atual.nota||comentario.trim()!==(atual.comentario||'');
 return <><div className="page-title"><span className="eyebrow">Sua opinião faz conexão</span><h1>Avaliar a plataforma</h1><p>Conte como está sendo sua experiência com o NEURON. Sua opinião ajuda a melhorar este espaço.</p></div><div className="evaluation-layout"><section className="card evaluation-card"><div className="card-heading"><span className="feature-icon evaluation-icon"><Icon name="star" size={24}/></span><div><h2>Como foi estudar por aqui?</h2><p>Avalie sua experiência com a plataforma.</p></div></div>{loading?<p role="status">Carregando sua avaliação…</p>:falhaCarga?<div><p className="alert error" role="alert">{erro}</p><button className="secondary" onClick={()=>setTentativa(t=>t+1)}>Tentar novamente</button></div>:<form onSubmit={salvar}><fieldset className="rating-fieldset" disabled={busy}><legend>Que nota você dá ao NEURON?</legend><div className="rating-options">{[1,2,3,4,5].map(valor=><label key={valor} className={`rating-option ${nota>=valor?'filled':''}`}><input type="radio" name="nota-plataforma" value={valor} checked={nota===valor} onChange={()=>{setNota(valor);setSucesso(false);}} aria-label={`${valor} ${valor===1?'estrela':'estrelas'} — ${notas[valor]}`}/><span><Icon name="star" size={32}/></span></label>)}</div><p className={`rating-caption ${nota?'selected':''}`} aria-live="polite">{nota?`${nota}/5 · ${notas[nota]}`:'Selecione de 1 a 5 estrelas'}</p></fieldset><label htmlFor="comentario-avaliacao" className="evaluation-label">O que podemos melhorar? <span>Opcional</span></label><textarea id="comentario-avaliacao" rows="5" maxLength="2000" value={comentario} onChange={e=>{setComentario(e.target.value);setSucesso(false);}} disabled={busy} placeholder="Conte o que ajudou nos seus estudos ou o que poderia funcionar melhor…"/><div className="evaluation-counter">{comentario.length}/2000</div>{erro&&<p className="alert error" role="alert">{erro}</p>}{sucesso&&<div className="evaluation-success" role="status" ref={mensagemRef} tabIndex={-1}><Icon name="check" size={20}/><div><strong>Obrigado pela sua avaliação!</strong><p>Sua opinião foi salva. Você pode atualizá-la quando quiser.</p></div></div>}<button type="submit" className="evaluation-submit" disabled={!nota||busy||!alterada}>{busy?'Salvando…':atual?'Atualizar avaliação':'Enviar avaliação'}<Icon name="arrow" size={17}/></button>{atual&&!sucesso&&<p className="evaluation-saved"><Icon name="check" size={13}/> Você já avaliou a plataforma. Pode atualizar sua resposta aqui.</p>}</form>}{loading&&erro&&<p className="alert error" role="alert">{erro}</p>}</section><aside className="evaluation-aside"><span className="feature-icon green"><Icon name="chat" size={25}/></span><h2>Uma plataforma melhor,<br/>com a sua ajuda.</h2><p>Seu retorno ajuda a entender o que funciona e o que pode melhorar no dia a dia de estudo.</p><ul><li><Icon name="check" size={16}/> Facilidade para encontrar os conteúdos</li><li><Icon name="check" size={16}/> Clareza das explicações do Monitor Virtual</li><li><Icon name="check" size={16}/> Experiência com questões e materiais</li></ul><div className="evaluation-privacy"><Icon name="shield" size={17}/><span>Sua avaliação é pública: seu nome, nota, comentário e data ficam visíveis na página de avaliações.</span></div></aside></div></>;
}
