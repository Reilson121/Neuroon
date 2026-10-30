import React,{useState} from 'react';
import useSessaoPratica from '../hooks/useSessaoPratica.js';
import {requisitar} from '../api.js';

export function ProvaDesign({sessao,Texto,Correcao,onConcluir,rotulo='Autoral · Design'}){
 const [respostas,setRespostas]=useState({}),[correcoes,setCorrecoes]=useState({});
 const [busy,setBusy]=useState(false),[travada,setTravada]=useState(false),[erro,setErro]=useState('');
 const completas=sessao.questoes.every(q=>respostas[q.id]);
 const concluida=sessao.questoes.every(q=>correcoes[q.id]);
 async function finalizar(e){
  e.preventDefault();if(!completas||busy||concluida)return;
  setBusy(true);setTravada(true);setErro('');
  const pendentes=sessao.questoes.filter(q=>!correcoes[q.id]);
  const resultados=await Promise.allSettled(pendentes.map(async q=>[q.id,await requisitar(`/api/v1/pratica/sessoes/${sessao.sessaoId}/respostas`,{method:'POST',body:{questaoId:q.id,alternativa:respostas[q.id]}})]));
  const novas={...correcoes};
  resultados.forEach(r=>{if(r.status==='fulfilled')novas[r.value[0]]=r.value[1];});
  setCorrecoes(novas);setBusy(false);
  if(sessao.questoes.every(q=>novas[q.id]))onConcluir();
  else setErro('Não foi possível concluir a correção. Suas escolhas foram mantidas. Tente finalizar novamente; se a sessão expirou, inicie outro simulado.');
 }
 const acertos=Object.values(correcoes).filter(c=>c.correto).length;
 return <>
  {concluida&&<section className="card exam-result" role="status"><h2>Resultado do simulado</h2><p className="exam-score">{acertos} de {sessao.questoes.length} acertos · {Math.round(acertos/sessao.questoes.length*100)}%</p><p>Confira abaixo sua escolha, o gabarito e a explicação de cada questão. A pontuação representa a proporção de acertos do simulado.</p></section>}
  <form onSubmit={finalizar}>
   <p role="status">{concluida?'Simulado concluído':`${Object.keys(respostas).length} de ${sessao.questoes.length} questões respondidas`}</p>
   {sessao.questoes.map((q,i)=><article className="question card" key={q.id}>
    <div className="eyebrow">Questão {i+1} de {sessao.questoes.length}<span className="badge">{rotulo}</span></div>
    <Texto>{q.enunciado}</Texto>
    <fieldset disabled={travada||busy||concluida}><legend className="sr-only">Resposta da questão {i+1}</legend>
     {Object.entries(q.alternativas).map(([letra,texto])=><label className={`option ${respostas[q.id]===letra?'selected':''}`} key={letra}><input type="radio" name={q.id} value={letra} checked={respostas[q.id]===letra} onChange={()=>setRespostas({...respostas,[q.id]:letra})}/><span className="letter">{letra}</span><span><Texto inline>{texto}</Texto></span></label>)}
    </fieldset>
    {concluida&&<><p><strong>Sua resposta: {respostas[q.id]}</strong></p><Correcao dados={correcoes[q.id]}/></>}
   </article>)}
   {erro&&<p className="alert error" role="alert">{erro}</p>}
   {!concluida&&<div className="card"><p>Você pode revisar suas escolhas antes de finalizar. O gabarito e as explicações serão exibidos ao concluir a correção de toda a prova.</p><button disabled={!completas||busy}>{busy?'Corrigindo simulado…':travada?'Tentar finalizar novamente':'Finalizar simulado'}</button></div>}
  </form>
 </>;
}

export default function DesignPratica({disciplina,assuntoId,assuntos,Texto,Questao,Correcao}){
 const [tipo,setTipo]=useState('PRATICA'),[selecionados,setSelecionados]=useState(assuntoId?[assuntoId]:[]),[quantidade,setQuantidade]=useState(5);
 const [terminou,setTerminou]=useState(false),[encerrada,setEncerrada]=useState(false);
 const simulado=tipo==='SIMULADO';
 const {sessao,busy,erro,iniciar}=useSessaoPratica({disciplinaId:disciplina.id,assuntoId:simulado?null:assuntoId,assuntoIds:simulado?selecionados:undefined,habilitada:disciplina.possuiProva,modo:'GERADAS_IA',origem:'MISTO',quantidade});
 const emProva=simulado&&!!sessao?.questoes.length&&!terminou;
 const invalida=simulado&&(!selecionados.length||quantidade<selecionados.length);
 function alternar(id){setSelecionados(xs=>xs.includes(id)?xs.filter(x=>x!==id):[...xs,id]);}
 async function comecar(revisar=false){setTerminou(false);setEncerrada(false);await iniciar(revisar);}
 if(!disciplina.possuiProva)return <div className="empty card"><h3>Prática ainda não habilitada</h3><p>A atualização da disciplina ainda não está disponível neste servidor.</p></div>;
 return <>
  <section className="card practice-controls"><h2>Design em situações reais</h2><p>Analise problemas, interprete as evidências e escolha a decisão mais adequada. Questões autorais inspiradas no formato contextualizado do ENEM, com cinco alternativas.</p>
   <p className="notice">Ainda não há prova do professor como referência. Os exercícios usam os conteúdos das aulas; não reproduzem questões oficiais nem garantem o estilo da avaliação da disciplina.</p>
   <div className="controls"><label>Atividade<select value={tipo} disabled={busy||emProva} onChange={e=>{setTipo(e.target.value);setTerminou(false);}}><option value="PRATICA">Prática com correção por questão</option><option value="SIMULADO">Prova simulada por conteúdos</option></select></label>
    <label>Quantidade<select value={quantidade} disabled={busy||emProva} onChange={e=>setQuantidade(Number(e.target.value))}>{[1,3,5,10].map(n=><option key={n}>{n}</option>)}</select></label>
   </div>
   {simulado&&<fieldset className="exam-topics" disabled={busy||emProva}><legend>Conteúdos do simulado</legend><p>Selecione um ou mais conteúdos abaixo. Esta seleção define o simulado, independentemente do assunto no topo da página. Haverá pelo menos uma questão por conteúdo escolhido.</p><div className="topic-grid">{assuntos.map(a=><label className="topic-choice" key={a.id}><input type="checkbox" checked={selecionados.includes(a.id)} onChange={()=>alternar(a.id)}/><span>{a.nome}</span></label>)}</div>{!assuntos.length&&<p>Não há conteúdos disponíveis nesta disciplina.</p>}</fieldset>}
   {simulado&&!selecionados.length&&<p role="status">Escolha pelo menos um conteúdo.</p>}
   {simulado&&quantidade<selecionados.length&&<p role="alert">Escolha uma quantidade de questões igual ou maior que o número de conteúdos.</p>}
   <p className="tip">{simulado?'A correção e a pontuação aparecem ao finalizar. Você poderá rever suas escolhas antes de entregar.':'Responda no seu ritmo e confira a explicação depois de cada questão.'}</p>
   <button disabled={busy||emProva||invalida} onClick={()=>comecar()}>{busy?'Preparando questões…':simulado?'Iniciar simulado':sessao?'Nova prática':'Iniciar prática'}</button>
   {emProva&&<button className="secondary" onClick={()=>{setTerminou(true);setEncerrada(true);}}>Encerrar tentativa sem concluir</button>}
  </section>
  {erro&&<p className="alert error" role="alert">{erro}</p>}
  {busy&&<p role="status">Preparando sua atividade…</p>}
  {sessao?.estado==='SEM_QUESTOES'&&<section className="card empty"><h3>Nenhuma questão nova nesta seleção</h3><p>{sessao.mensagem}</p><button disabled={busy||invalida} onClick={()=>comecar(true)}>Revisar questões já vistas</button></section>}
  {sessao?.questoes.length>0&&sessao.questoes.length<quantidade&&<p className="notice">Esta seleção reuniu {sessao.questoes.length} questões das {quantidade} solicitadas. A atividade usa somente as questões disponíveis e não repete itens para completar a quantidade.</p>}
  {encerrada&&<p role="status">Tentativa encerrada. Você pode configurar um novo simulado.</p>}
  {simulado?(sessao?.questoes.length>0&&!encerrada&&<ProvaDesign key={sessao.sessaoId} sessao={sessao} Texto={Texto} Correcao={Correcao} onConcluir={()=>setTerminou(true)}/>):sessao?.questoes.map((q,i)=><Questao key={`${sessao.sessaoId}-${q.id}`} questao={q} sessaoId={sessao.sessaoId} indice={i} total={sessao.questoes.length}/>)}
 </>;
}
