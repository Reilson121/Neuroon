// O navegador fala exclusivamente com a API pública do Spring Boot.
let csrf;
export async function renovarCsrf(){
  const r=await fetch('/api/v1/auth/csrf',{credentials:'include'});
  if(!r.ok)throw new Error('Não foi possível iniciar uma conexão segura.');
  csrf=await r.json();
}
export async function requisitar(path,{method='GET',body,signal}={}){
  if(!path.startsWith('/api/v1/'))throw new Error('Destino de API inválido.');
  const headers={'Accept':'application/json'};
  if(method!=='GET'){
    if(!csrf)await renovarCsrf();
    headers[csrf.headerName]=csrf.token;
  }
  if(body!==undefined)headers['Content-Type']='application/json';
  const r=await fetch(path,{method,headers,credentials:'include',body:body===undefined?undefined:JSON.stringify(body),signal});
  if(!r.ok){
    let data;try{data=await r.json();}catch{data={};}
    const e=new Error(data.mensagem || (r.status===401?'Sua sessão terminou. Entre novamente.':'Não foi possível concluir. Tente novamente.'));
    e.status=r.status;throw e;
  }
  return r.status===204?null:r.json();
}
export async function conversar(body,onEvent,signal){
  if(!csrf)await renovarCsrf();
  const r=await fetch('/api/v1/monitor/chat',{method:'POST',credentials:'include',signal,
    headers:{'Content-Type':'application/json','Accept':'text/event-stream',[csrf.headerName]:csrf.token},body:JSON.stringify(body)});
  if(!r.ok){let d;try{d=await r.json();}catch{d={};}throw new Error(d.mensagem||'Não foi possível consultar o Monitor.');}
  const reader=r.body.getReader(),decoder=new TextDecoder();let buffer='';let terminou=false;
  while(true){
    const {value,done}=await reader.read();buffer+=decoder.decode(value||new Uint8Array(),{stream:!done}).replace(/\r\n/g,'\n');
    let end;
    while((end=buffer.indexOf('\n\n'))>=0){
      const event=buffer.slice(0,end);buffer=buffer.slice(end+2);
      const name=event.split('\n').find(l=>l.startsWith('event:'))?.slice(6).trim();
      const data=event.split('\n').filter(l=>l.startsWith('data:')).map(l=>l.slice(5).trimStart()).join('\n');
      if(name&&data){onEvent(name,JSON.parse(data));if(name==='done')terminou=true;}
    }
    if(done)break;
  }
  if(!terminou)throw new Error('A conexão terminou antes de completar a resposta. Tente novamente.');
}
