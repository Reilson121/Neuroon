import React from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import referenciasLegiveis from './referenciasLegiveis.js';
import 'katex/dist/katex.min.css';
import './Texto.css';

// Keep math explicit: slashes in prose, URLs and code are not fractions.
export default function Texto({children,inline=false,ocultarReferencias=false}){
 return <Markdown
  remarkPlugins={[remarkGfm,remarkMath,...(ocultarReferencias?[referenciasLegiveis]:[])]}
  rehypePlugins={[[rehypeKatex,{trust:false,strict:'ignore',throwOnError:false}]]}
  components={inline?{p:({children})=><span>{children}</span>}:undefined}
 >{children||''}</Markdown>;
}
