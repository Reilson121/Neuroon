import React,{useState} from 'react';
import useSessaoPratica from '../hooks/useSessaoPratica.js';
import {ProvaDesign} from './DesignPratica.jsx';
import topicosI from '../calculo-topicos.json';
import topicosII from '../integral-topicos.json';

const atividades={PRATICA:'Prática com correção por questão',ASSUNTOS:'Prova por assuntos selecionados',UNIDADE_1:'Prova da 1ª unidade',UNIDADE_2:'Prova da 2ª unidade',FINAL:'Prova final · duas unidades',SEGUNDA_CHAMADA:'Segunda chamada · duas unidades'};
export default function CalculoPratica({disciplina,assuntoId,assuntos,materiais,Texto,Correcao,PraticaGeral}){
 const integral=disciplina.nome==='Cálculo para Computação II';
 const topicos=integral?topicosII:topicosI;
 const tabela=integral?materiais.find(m=>m.titulo.includes('Tabela de Integrais')):null;
 const [tipo,setTipo]=useState('PRATICA'),[selecionados,setSelecionados]=useState(assuntoId&&(!integral||assuntos.find(a=>a.id===assuntoId)?.ordem!==8)?[assuntoId]:[]),[quantidade,setQuantidade]=useState(10);
 const [terminou,setTerminou]=useState(false),[encerrada,setEncerrada]=useState(false);
 const simulado=tipo!=='PRATICA',unidade=tipo==='UNIDADE_1'?1:tipo==='UNIDADE_2'?2:0;
 const ordens=[...new Set(topicos.filter(t=>(!integral||t.unidade>0)&&(!unidade||t.unidade===unidade)).map(t=>t.assuntoOrdem))];
 const elegiveis=assuntos.filter(a=>ordens.includes(a.ordem));
 const ids=tipo==='ASSUNTOS'?selecionados:elegiveis.map(a=>a.id);
 const faltantes=tipo!=='ASSUNTOS'&&ordens.some(ordem=>!elegiveis.some(a=>a.ordem===ordem));
 const invalida=!ids.length||quantidade<ids.length||faltantes;
 const {sessao,busy,erro,iniciar}=useSessaoPratica({disciplinaId:disciplina.id,assuntoId:null,assuntoIds:ids,habilitada:simulado&&disciplina.possuiProva,modo:'GERADAS_IA',origem:'MISTO',quantidade,unidadeCalculo:unidade,topicoCalculo:'MISTO',tipoFuncao:'MISTO',chaveAtividade:tipo});
 const emProva=simulado&&!!sessao?.questoes.length&&!terminou;
 function alternar(id){setSelecionados(xs=>xs.includes(id)?xs.filter(x=>x!==id):[...xs,id]);}
 async function comecar(){setTerminou(false);setEncerrada(false);await iniciar();}
 return <>
  <section className="card practice-controls"><h2>Prática e provas de Cálculo</h2>
   <div className="controls"><label>Atividade<select value={tipo} disabled={busy||emProva} onChange={e=>{setTipo(e.target.value);setTerminou(false);setEncerrada(false);}}>{Object.entries(atividades).map(([id,nome])=><option key={id} value={id}>{nome}</option>)}</select></label>
   {simulado&&<label>Quantidade de questões<select value={quantidade} disabled={busy||emProva} onChange={e=>setQuantidade(Number(e.target.value))}>{[1,3,5,10].map(n=><option key={n}>{n}</option>)}</select></label>}</div>
   {simulado&&<>
    {integral&&tabela?.arquivoDisponivel&&<p className="tip"><a href={`/api/v1/materiais/${tabela.id}/arquivo`} target="_blank" rel="noopener noreferrer">Abrir tabela de integrais</a> para consulta durante o simulado.</p>}
    {integral?<p className="notice">Simulado autoral de estudo: esta disciplina não tem prova oficial. Comandos diretos inspirados no formato de Cálculo I, adaptados para cinco alternativas. A 1ª unidade cobra somente integrais de uma variável; a 2ª reúne duplas e triplas diretas em cartesianas. O complemento de várias variáveis fica fora dos simulados padrão.</p>:<>
    <p>Exercícios com comandos diretos de cálculo, inspirados na prova disponível da 1ª unidade. Resolva no papel e marque as alternativas para conferir ao entregar. O exemplo do professor usa questões abertas; este simulado adapta o formato para cinco alternativas.</p>
    <p className="notice">Não há prova do professor da 2ª unidade: as questões de derivadas seguem os livros e a tabela fornecidos. A prova final e a segunda chamada abrangem as duas unidades. Este é um simulado de estudo, sem garantia de reproduzir a avaliação oficial.</p></>}
    {tipo==='ASSUNTOS'?<fieldset className="exam-topics" disabled={busy||emProva}><legend>Assuntos da prova</legend><p>Escolha um ou mais assuntos. A seleção abaixo define a prova, independentemente do assunto no topo da página.</p><div className="topic-grid">{assuntos.filter(a=>topicos.some(t=>(!integral||t.unidade>0)&&t.assuntoOrdem===a.ordem)).map(a=><label className="topic-choice" key={a.id}><input type="checkbox" checked={selecionados.includes(a.id)} onChange={()=>alternar(a.id)}/><span>{a.nome}</span></label>)}</div></fieldset>:<div><h3>Assuntos incluídos</h3><ul>{elegiveis.map(a=><li key={a.id}>{a.nome}</li>)}</ul></div>}
    {!ids.length&&<p role="status">Escolha pelo menos um assunto disponível.</p>}
    {faltantes&&<p role="alert">O catálogo está incompleto para esta prova. Todos os assuntos da unidade precisam estar disponíveis.</p>}
    {quantidade<ids.length&&<p role="alert">Escolha uma quantidade de questões igual ou maior que o número de assuntos ({ids.length}).</p>}
    <p className="tip">Haverá pelo menos uma questão por assunto. A pontuação, o gabarito e as resoluções aparecem após finalizar toda a prova.</p>
    <button disabled={busy||emProva||invalida||!disciplina.possuiProva} onClick={comecar}>{busy?'Preparando e conferindo…':'Iniciar simulado'}</button>
    {emProva&&<button className="secondary" onClick={()=>{setTerminou(true);setEncerrada(true);}}>Encerrar tentativa sem concluir</button>}
   </>}
  </section>
  {!simulado?<PraticaGeral disciplina={disciplina} assuntoId={assuntoId} assuntos={assuntos} materiais={materiais}/>:<>
   {erro&&<p className="alert error" role="alert">{erro}</p>}
   {busy&&<p role="status">Preparando e conferindo a prova…</p>}
   {sessao?.estado==='SEM_QUESTOES'&&<section className="card empty"><h3>Não foi possível preparar esta prova</h3><p>{sessao.mensagem}</p></section>}
   {encerrada&&<p role="status">Tentativa encerrada. Você pode configurar uma nova prova.</p>}
   {sessao?.questoes.length>0&&!encerrada&&<ProvaDesign key={sessao.sessaoId} sessao={sessao} Texto={Texto} Correcao={Correcao} onConcluir={()=>setTerminou(true)} rotulo={atividades[tipo]}/>}
  </>}
 </>;
}
