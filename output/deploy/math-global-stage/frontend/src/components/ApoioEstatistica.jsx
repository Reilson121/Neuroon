import React,{useEffect,useState} from 'react';
import paginas from '../estatistica-paginas.json';

export default function ApoioEstatistica({materiais=[],assuntos=[],assuntoId}){
 const [escolha,setEscolha]=useState(assuntoId||'');
 useEffect(()=>setEscolha(assuntoId||''),[assuntoId]);
 const disponiveis=assuntos.filter(a=>paginas[a.ordem]);
 const atual=disponiveis.find(a=>a.id===Number(escolha))||disponiveis[0];
 const material=materiais.find(m=>m.tipo==='SLIDE_AULA'&&m.arquivoDisponivel&&m.assuntoId===atual?.id)||materiais.find(m=>m.tipo==='SLIDE_AULA'&&m.arquivoDisponivel);
 if(!material||!atual)return null;
 const intervalos=paginas[atual.ordem];
 return <details className="tip formula-support"><summary>Consultar fórmulas e tabelas de Estatística</summary>
  <p>Abra os slides originais para conferir a notação, as fórmulas e as tabelas deste conteúdo. As páginas abaixo são as páginas do PDF.</p>
  <label>Conteúdo da consulta<select value={atual.id} onChange={e=>setEscolha(Number(e.target.value))}>{disponiveis.map(a=><option key={a.id} value={a.id}>{a.nome}</option>)}</select></label>
  <ul>{intervalos.map(([inicio,fim])=><li key={inicio}><a href={`/api/v1/materiais/${material.id}/arquivo#page=${inicio}`} target="_blank" rel="noopener noreferrer">Abrir slides de {atual.nome} · {inicio===fim?`p. ${inicio}`:`pp. ${inicio}–${fim}`}</a></li>)}</ul>
 </details>;
}
