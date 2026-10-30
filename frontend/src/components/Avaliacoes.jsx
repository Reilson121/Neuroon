import React,{useEffect,useState} from 'react';
import {requisitar} from '../api.js';
import './Avaliacoes.css';

function horario(valor){
 if(!valor)return 'Data indisponível';
 return new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short',timeZone:'America/Fortaleza'}).format(new Date(`${valor}Z`));
}
export default function Avaliacoes(){
 const [pagina,setPagina]=useState(0),[revisao,setRevisao]=useState(0),[dados,setDados]=useState(null),[carregando,setCarregando]=useState(true),[erro,setErro]=useState('');
 useEffect(()=>{
  const controller=new AbortController();setCarregando(true);setErro('');setDados(null);
  requisitar(`/api/v1/avaliacoes?pagina=${pagina}`,{signal:controller.signal})
   .then(d=>{if(!controller.signal.aborted)setDados(d);})
   .catch(e=>{if(!controller.signal.aborted)setErro(e.message);})
   .finally(()=>{if(!controller.signal.aborted)setCarregando(false);});
  return()=>controller.abort();
 },[pagina,revisao]);
 return <section className="reviews-page">
  <div className="page-title"><span className="eyebrow">Opinião de quem estuda</span><h1>Avaliações dos alunos</h1><p>Acompanhe as opiniões recebidas sobre o NEURON.</p></div>
  <button className="secondary" disabled={carregando} onClick={()=>setRevisao(r=>r+1)}>Atualizar avaliações</button>
  {erro&&<p className="alert error" role="alert">{erro}</p>}
  {carregando?<p role="status">Carregando avaliações…</p>:dados&&<>
   <div className="reviews-summary" aria-label="Resumo das avaliações">
    <div className="card"><span>Avaliações recebidas</span><strong>{dados.total}</strong></div>
    <div className="card"><span>Nota média</span><strong>{dados.media==null?'—':`${dados.media.toLocaleString('pt-BR',{maximumFractionDigits:2})} / 5`}</strong></div>
    <div className="card"><span>Com comentário</span><strong>{dados.comComentario}</strong></div>
   </div>
   <p className="reviews-caption">Da mais recente para a mais antiga. Horários de Fortaleza. Cada aluno pode atualizar sua avaliação.</p>
   {!dados.total?<div className="card empty"><h2>Nenhuma avaliação recebida</h2><p>As respostas aparecerão aqui quando os alunos avaliarem a plataforma.</p></div>:<ul className="reviews-list">{dados.avaliacoes.map(a=><li className="card" key={a.id}>
    <div className="review-heading"><h2>{a.aluno}</h2><span className="review-rating" aria-label={`Nota ${a.nota} de 5`}><span aria-hidden="true">{'★'.repeat(a.nota)}{'☆'.repeat(5-a.nota)}</span> {a.nota}/5</span></div>
    <time dateTime={`${a.enviadoEm}Z`}>{horario(a.enviadoEm)}</time>
    <p className={a.comentario?'review-comment':'review-no-comment'}>{a.comentario||'Sem comentário.'}</p>
   </li>)}</ul>}
   {dados.totalPaginas>1&&<nav className="user-actions" aria-label="Páginas de avaliações"><button className="secondary" disabled={pagina===0} onClick={()=>setPagina(p=>p-1)}>Anterior</button><span>Página {pagina+1} de {dados.totalPaginas}</span><button className="secondary" disabled={pagina+1>=dados.totalPaginas} onClick={()=>setPagina(p=>p+1)}>Próxima</button></nav>}
  </>}
 </section>;
}
