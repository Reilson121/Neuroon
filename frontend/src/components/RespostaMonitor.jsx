import React from 'react';
import Texto from './Texto.jsx';
import Icon from './Icon.jsx';
import './RespostaMonitor.css';

const tituloFonte = fonte => fonte.tituloMaterial || fonte.titulo_material || fonte.arquivo || 'Material consultado';

export default function RespostaMonitor({conteudo,fontes=[]}){
 return <>
  <Texto ocultarReferencias>{conteudo}</Texto>
  {!!fontes.length && <details className="message-sources readable-sources">
   <summary><Icon name="book" size={14}/><span>De onde veio esta explicação?<small>{fontes.length} {fontes.length===1?'material consultado':'materiais consultados'}</small></span><Icon name="chevron" size={13}/></summary>
   <p className="sources-explanation">A explicação da IA se apoia nos materiais abaixo. Abra o documento para conferir o conteúdo na página indicada.</p>
   <ul className="readable-source-list" aria-label="Materiais usados nesta resposta">
    {fontes.map((fonte,i)=>{
     const titulo = tituloFonte(fonte);
     const materialId = fonte.materialId || fonte.material_id;
     const paginas = [...new Set([fonte.pagina,...(fonte.paginas_mescladas || [])].filter(Boolean))];
     const questao = fonte.numeroQuestao || fonte.numero_questao;
     return <li key={i}>
      <strong>{titulo}</strong>
      {!!paginas.length && <span>{paginas.length===1?'Página':'Páginas'} {paginas.join(', ')}</span>}
      {questao && <span>Questão {questao}</span>}
      {!!fonte.revisoes_ia?.length && <span>Inclui observação de IA.</span>}
      {materialId ? <a href={`/api/v1/materiais/${encodeURIComponent(materialId)}/arquivo${fonte.pagina?`#page=${encodeURIComponent(fonte.pagina)}`:''}`} target="_blank" rel="noopener noreferrer" aria-label={`Abrir material: ${titulo}`}>Abrir material<Icon name="arrow" size={12}/></a>
       : <span className="source-unavailable">Documento sem link disponível nesta conversa.</span>}
     </li>;
    })}
   </ul>
  </details>}
 </>;
}
