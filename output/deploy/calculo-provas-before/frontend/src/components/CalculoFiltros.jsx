import React from 'react';
import topicos from '../calculo-topicos.json';
const nomes={AFIM:'Afim',POLINOMIAL:'Polinomial',RACIONAL:'Racional',RADICAL:'Com radical',POR_PARTES:'Definida por partes',TRIGONOMETRICA:'Trigonométrica',EXPONENCIAL:'Exponencial',LOGARITMICA:'Logarítmica',HIPERBOLICA:'Hiperbólica',IMPLICITA:'Relação implícita'};
export default function CalculoFiltros({valor,onChange,busy,assuntoOrdem}){
 const disponiveis=topicos.filter(t=>!assuntoOrdem||t.assuntoOrdem===assuntoOrdem);
 const lista=disponiveis.filter(t=>!valor.unidadeCalculo||t.unidade===valor.unidadeCalculo);
 const tipos=[...new Set(lista.filter(t=>valor.topicoCalculo==='MISTO'||t.id===valor.topicoCalculo).flatMap(t=>t.tipos))];
 return <><label>Unidade<select value={valor.unidadeCalculo} disabled={busy} onChange={e=>onChange({unidadeCalculo:Number(e.target.value),topicoCalculo:'MISTO',tipoFuncao:'MISTO'})}><option value={0}>Todas as unidades da seleção</option>{[1,2].filter(u=>disponiveis.some(t=>t.unidade===u)).map(u=><option key={u} value={u}>{u===1?'1ª unidade · Funções e limites':'2ª unidade · Derivadas'}</option>)}</select></label>
 <label>Tópico ou regra<select value={valor.topicoCalculo} disabled={busy} onChange={e=>onChange({...valor,topicoCalculo:e.target.value,tipoFuncao:'MISTO'})}><option value="MISTO">Todos os tópicos da seleção</option>{lista.map(t=><option key={t.id} value={t.id}>{t.nome}</option>)}</select></label>
 <label>Tipo de função<select value={valor.tipoFuncao} disabled={busy} onChange={e=>onChange({...valor,tipoFuncao:e.target.value})}><option value="MISTO">Tipos variados</option>{tipos.map(t=><option key={t} value={t}>{nomes[t]}</option>)}</select></label></>;
}
