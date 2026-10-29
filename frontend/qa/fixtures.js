// Somente para a validação visual no servidor de desenvolvimento.
// Esta página não faz parte da entrada de produção (index.html).
import catalogo from './catalogo.json';
const originalFetch=globalThis.fetch.bind(globalThis);
const disciplina=catalogo.disciplinas.find(d=>d.slug==='estatistica');
const fontes=[{referencia:'F1',arquivo:'Aula 1 — Fundamentos de probabilidade.pdf',pagina:12}];
const resumo={id:'visual-1',titulo:'Como funciona a probabilidade condicional?',disciplinaId:disciplina.id,assuntoId:null,atualizadoEm:new Date().toISOString()};
const salvas=[{id:1,papel:'USUARIO',conteudo:'Como funciona a probabilidade condicional?',fontes:[],criadoEm:new Date().toISOString()},{id:2,papel:'MONITOR',conteudo:'A **probabilidade condicional** representa a chance de um evento ocorrer quando já sabemos que outro evento aconteceu. [F1]\n\nA expressão é P(A | B) = P(A ∩ B) / P(B), para P(B) > 0. [F1]',fontes,criadoEm:new Date().toISOString()}];
let avaliacao=null;
const modo=new URLSearchParams(location.search);
let sessaoPreview=modo.get('tela')==='entrada'?null:{id:99,nome:'Mariana Oliveira',email:'mariana@example.test',perfil:modo.get('perfil')==='admin'?'ADMINISTRADOR':'ESTUDANTE'};
let usuariosPreview=[{id:99,nome:'Mariana Oliveira',email:'mariana@example.test',perfil:'ADMINISTRADOR'},{id:100,nome:'Ana Silva',email:'ana@example.test',perfil:'ESTUDANTE'},{id:101,nome:'Lucas Santos',email:'lucas@example.test',perfil:'ESTUDANTE'}];
let proximoId=102;
globalThis.fetch=async(input,options={})=>{
 const url=new URL(typeof input==='string'?input:input.url,location.href),path=url.pathname;
 if(!path.startsWith('/api/'))return originalFetch(input,options);
 const json=data=>Promise.resolve(new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}}));
 if(path==='/api/v1/auth/me')return sessaoPreview?json(sessaoPreview):new Response(null,{status:401});
 if(path==='/api/v1/auth/cadastro')return json({id:proximoId++,...JSON.parse(options.body),senha:undefined,perfil:'ESTUDANTE'});
 if(path==='/api/v1/auth/login'){sessaoPreview={id:100,nome:'Ana Silva',email:JSON.parse(options.body).email,perfil:'ESTUDANTE'};return json(sessaoPreview);}
 if(path==='/api/v1/admin/usuarios'||path.startsWith('/api/v1/admin/usuarios/')){
  const id=Number(path.split('/')[5]),method=options.method||'GET';
  if(method==='POST'){const {nome,email}=JSON.parse(options.body);const novo={id:proximoId++,nome,email,perfil:'ESTUDANTE'};usuariosPreview.push(novo);return json(novo);}
  if(method==='DELETE'){usuariosPreview=usuariosPreview.filter(u=>u.id!==id);return new Response(null,{status:204});}
  if(method==='PUT'){const {nome,email}=JSON.parse(options.body);usuariosPreview=usuariosPreview.map(u=>u.id===id?{...u,nome,email}:u);return json(usuariosPreview.find(u=>u.id===id));}
  if(id)return json(usuariosPreview.find(u=>u.id===id));
  const pagina=Number(url.searchParams.get('pagina')||0);return json({usuarios:usuariosPreview.slice(pagina*10,pagina*10+10),pagina,totalPaginas:Math.ceil(usuariosPreview.length/10),total:usuariosPreview.length});
 }
 if(path==='/api/v1/auth/csrf')return json({headerName:'X-CSRF-TOKEN',token:'visual-fixture'});
 if(path==='/api/v1/avaliacao-plataforma/minha'){
  if(options.method==='PUT'){const entrada=JSON.parse(options.body);avaliacao={nota:entrada.nota,comentario:entrada.comentario,enviadoEm:new Date().toISOString()};}
  return avaliacao?json(avaliacao):new Response(null,{status:204});
 }
 if(path==='/api/v1/auth/logout'){sessaoPreview=null;return new Response(null,{status:204});}
 if(path==='/api/v1/periodos')return json(catalogo.periodos);
 const porPeriodo=path.match(/^\/api\/v1\/periodos\/(\d+)\/disciplinas$/);
 if(porPeriodo)return json(catalogo.disciplinas.filter(d=>d.periodoId===Number(porPeriodo[1])));
 const porDisciplina=path.match(/^\/api\/v1\/disciplinas\/(\d+)\/(assuntos|materiais)$/);
 if(porDisciplina){
  const dados=porDisciplina[2]==='assuntos'?catalogo.assuntos:catalogo.materiais;
  const assunto=Number(url.searchParams.get('assuntoId'));
  return json(dados.filter(item=>item.disciplinaId===Number(porDisciplina[1])&&(!assunto||!item.assuntoId||item.assuntoId===assunto)));
 }
 if(path==='/api/v1/monitor/conversas')return json(Number(url.searchParams.get('disciplinaId'))===disciplina.id&&!url.searchParams.get('assuntoId')?[resumo]:[]);
 if(path.startsWith('/api/v1/monitor/conversas/'))return json({conversa:resumo,mensagens:salvas});
 if(path==='/api/v1/monitor/chat'){
  const entrada=JSON.parse(options.body);
  const selecionada=catalogo.disciplinas.find(d=>d.id===entrada.disciplinaId);
  const resposta=`Esta é uma prévia visual de ${selecionada?.nome||'sua disciplina'}. O catálogo está completo nesta demonstração, mas as respostas de IA, os PDFs e o histórico real exigem a aplicação conectada aos serviços. Nenhuma consulta à IA foi realizada.`;
  const exemploEstatistica=entrada.disciplinaId===disciplina.id&&!entrada.assuntoId;
  if(exemploEstatistica)salvas.push({id:salvas.length+1,papel:'USUARIO',conteudo:entrada.pergunta,fontes:[],criadoEm:new Date().toISOString()},{id:salvas.length+2,papel:'MONITOR',conteudo:resposta,fontes:[],criadoEm:new Date().toISOString()});
  return new Response([['token',{texto:resposta}],['sources',{fontes:[]}],['done',{threadId:exemploEstatistica?resumo.id:null}]].map(([event,data])=>`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`).join(''),{headers:{'Content-Type':'text/event-stream'}});
 }
 if(path==='/api/v1/pratica/sessoes'){
  const entrada=JSON.parse(options.body);
  const fundamentos=catalogo.assuntos.find(a=>a.disciplinaId===disciplina.id&&a.ordem===1);
  if(entrada.disciplinaId!==disciplina.id||(entrada.assuntoId&&entrada.assuntoId!==fundamentos.id))return json({sessaoId:'visual-pratica',questoes:[],estado:'SEM_QUESTOES',mensagem:'A prévia só demonstra uma questão de fundamentos de probabilidade. Use a aplicação conectada para praticar os demais conteúdos.'});
  return json({sessaoId:'visual-pratica',questoes:[{id:'visual-q1',enunciado:'Em uma urna há **3 bolas azuis e 2 bolas verdes**. Ao retirar uma bola ao acaso, qual é a probabilidade de ela ser azul?',alternativas:{A:'1/5',B:'2/5',C:'3/5',D:'4/5',E:'1'},origem:'GERADA_IA',fontes}],estado:'DISPONIVEL'});
 }
 if(path.includes('/respostas'))return json({correto:true,alternativaCorreta:'C',conceito:'Probabilidade clássica',formula:'P(A) = casos favoráveis / casos possíveis',substituicao:'P(azul) = 3 / 5',calculos:['Total de bolas: 3 + 2 = 5','Bolas azuis: 3','Probabilidade: 3/5 = 0,6 = 60%'],resolucao:'A chance de retirar uma bola azul é de 60%.',errosComuns:['Usar apenas as bolas verdes como total.'],dica:'Conte todos os resultados possíveis antes de dividir.',fontes});
 return new Response(JSON.stringify({mensagem:'Rota não prevista nesta validação visual.'}),{status:404});
};
await import('/src/main.jsx');
const aviso=document.createElement('div');
aviso.style.cssText='position:fixed;bottom:12px;right:12px;z-index:1000;background:#fff;border:1px solid #dfe5ef;border-radius:10px;padding:10px 14px;box-shadow:0 3px 18px #0c1e3a18;font:12px Segoe UI,sans-serif';
aviso.innerHTML='Prévia visual · catálogo local · IA simulada &nbsp; <a href="?tela=entrada">Cadastro</a> · <a href="?perfil=admin">Administração</a>';
document.body.append(aviso);
