import {useCallback,useEffect,useRef,useState} from 'react';
import {requisitar} from '../api.js';

// Uma resposta só pode atualizar a seleção que originou sua requisição.
export default function useSessaoPratica({disciplinaId,assuntoId,habilitada,modo,origem,quantidade}){
 const chave=JSON.stringify([disciplinaId,assuntoId??null,habilitada,modo,origem,quantidade]);
 const [estado,setEstado]=useState({chave,sessao:null,busy:false,erro:''});
 const sequencia=useRef(0),pendente=useRef(null);
 useEffect(()=>{
  setEstado({chave,sessao:null,busy:false,erro:''});
  return()=>{sequencia.current++;pendente.current?.controller.abort();pendente.current=null;};
 },[chave]);
 const iniciar=useCallback(async(revisarVistas=false)=>{
  if(!habilitada||pendente.current?.chave===chave)return;
  pendente.current?.controller.abort();
  const controller=new AbortController(),seq=++sequencia.current;
  pendente.current={controller,chave};
  setEstado({chave,sessao:null,busy:true,erro:''});
  try{
   const sessao=await requisitar('/api/v1/pratica/sessoes',{
    method:'POST',signal:controller.signal,
    body:{disciplinaId,assuntoId:assuntoId??null,modo,origem,quantidade,revisarVistas},
   });
   if(seq===sequencia.current&&!controller.signal.aborted)setEstado({chave,sessao,busy:false,erro:''});
  }catch(e){
   if(seq===sequencia.current&&!controller.signal.aborted&&e.name!=='AbortError')setEstado({chave,sessao:null,busy:false,erro:e.message});
  }finally{
   if(seq===sequencia.current)pendente.current=null;
  }
 },[chave,disciplinaId,assuntoId,habilitada,modo,origem,quantidade]);
 return {...(estado.chave===chave?estado:{sessao:null,busy:false,erro:''}),iniciar};
}
