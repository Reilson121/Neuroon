import React,{useEffect,useState} from 'react';
import {requisitar} from '../api.js';

export function CamposUsuario({dados,setDados,edicao=false,disabled=false}){
 const alterar=campo=>e=>setDados({...dados,[campo]:e.target.value});
 return <fieldset className="user-fields" disabled={disabled}>
  <legend className="sr-only">Dados do usuário</legend>
  <label>Nome completo<input required maxLength={150} autoComplete="name" value={dados.nome} onChange={alterar('nome')}/></label>
  <label>Email<input type="email" required maxLength={255} autoComplete="email" value={dados.email} onChange={alterar('email')}/></label>
  <label>{edicao?'Nova senha (opcional)':'Senha'}<input type="password" required={!edicao} minLength={8} maxLength={72} autoComplete="new-password" value={dados.senha} onChange={alterar('senha')}/></label>
  <small>{edicao?'Deixe a senha vazia para manter a atual.':'Use pelo menos 8 caracteres.'}</small>
 </fieldset>;
}

export default function Usuarios(){
 const [lista,setLista]=useState(null),[pagina,setPagina]=useState(0),[revisao,setRevisao]=useState(0);
 const [form,setForm]=useState(null),[exclusao,setExclusao]=useState(null),[busy,setBusy]=useState(false),[carregando,setCarregando]=useState(true),[erro,setErro]=useState(''),[aviso,setAviso]=useState('');
 useEffect(()=>{let ativo=true;setCarregando(true);setErro('');
  requisitar(`/api/v1/admin/usuarios?pagina=${pagina}`).then(d=>{if(ativo)setLista(d);}).catch(e=>{if(ativo){setLista(null);setErro(e.message);}}).finally(()=>{if(ativo)setCarregando(false);});
  return()=>{ativo=false;};
 },[pagina,revisao]);
 function novo(){setForm({nome:'',email:'',senha:''});setExclusao(null);setErro('');setAviso('');}
 async function editar(id){setBusy(true);setErro('');setAviso('');try{const u=await requisitar(`/api/v1/admin/usuarios/${id}`);setForm({...u,senha:''});setExclusao(null);}catch(e){setErro(e.message);}finally{setBusy(false);}}
 async function salvar(e){e.preventDefault();setBusy(true);setErro('');setAviso('');try{
  await requisitar(`/api/v1/admin/usuarios${form.id?`/${form.id}`:''}`,{method:form.id?'PUT':'POST',body:{nome:form.nome,email:form.email,senha:form.senha}});
  setAviso(form.id?'Usuário atualizado.':'Usuário cadastrado.');setForm(null);setRevisao(r=>r+1);
 }catch(e){setErro(e.message);}finally{setBusy(false);}}
 async function excluir(){setBusy(true);setErro('');setAviso('');try{
  await requisitar(`/api/v1/admin/usuarios/${exclusao.id}`,{method:'DELETE'});setExclusao(null);setAviso('Usuário excluído. O acesso à conta foi desativado.');
  if(lista.usuarios.length===1&&pagina>0)setPagina(p=>p-1);else setRevisao(r=>r+1);
 }catch(e){setErro(e.message);}finally{setBusy(false);}}
 return <section className="users-page">
  <div className="page-title"><span className="eyebrow">Administração</span><h1>Usuários</h1><p>Cadastre e gerencie as contas de estudantes.</p></div>
  {erro&&<p className="alert error" role="alert">{erro}</p>}{aviso&&<p className="notice" role="status">{aviso}</p>}
  <button onClick={novo} disabled={busy}>Novo usuário</button>
  {form&&<form className="card user-form" onSubmit={salvar}><h2>{form.id?'Editar usuário':'Cadastrar usuário'}</h2><CamposUsuario dados={form} setDados={setForm} edicao={!!form.id} disabled={busy}/><div className="user-actions"><button disabled={busy}>{busy?'Salvando…':'Salvar usuário'}</button><button type="button" className="secondary" disabled={busy} onClick={()=>setForm(null)}>Cancelar</button></div></form>}
  {exclusao&&<section className="card user-form" aria-label="Confirmar exclusão"><h2>Excluir {exclusao.nome}?</h2><p>A conta perderá acesso. O histórico acadêmico será preservado.</p><div className="user-actions"><button className="danger" disabled={busy} onClick={excluir}>Confirmar exclusão</button><button className="secondary" disabled={busy} onClick={()=>setExclusao(null)}>Cancelar exclusão</button></div></section>}
  {carregando?<p role="status">Carregando usuários…</p>:lista&&<div className="card users-list"><p>{lista.total} usuário(s) cadastrado(s)</p>
   {!lista.usuarios.length?<p>Nenhum usuário cadastrado.</p>:<ul>{lista.usuarios.map(u=><li key={u.id}><div><strong>{u.nome}</strong><span>{u.email}</span><small>{u.perfil==='ADMINISTRADOR'?'Administrador · conta protegida':'Estudante'}</small></div>{u.perfil==='ESTUDANTE'&&<div className="user-actions"><button className="secondary" disabled={busy} onClick={()=>editar(u.id)} aria-label={`Editar ${u.nome}`}>Editar</button><button className="secondary" disabled={busy} onClick={()=>{setExclusao(u);setForm(null);setErro('');setAviso('');}} aria-label={`Excluir ${u.nome}`}>Excluir</button></div>}</li>)}</ul>}
   {lista.totalPaginas>1&&<nav className="user-actions" aria-label="Páginas de usuários"><button className="secondary" disabled={busy||pagina===0} onClick={()=>setPagina(p=>p-1)}>Anterior</button><span>Página {pagina+1} de {lista.totalPaginas}</span><button className="secondary" disabled={busy||pagina+1>=lista.totalPaginas} onClick={()=>setPagina(p=>p+1)}>Próxima</button></nav>}
  </div>}
 </section>;
}
