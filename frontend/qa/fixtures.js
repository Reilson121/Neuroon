// Somente para a validação visual no servidor de desenvolvimento.
// Esta página não faz parte da entrada de produção (index.html).
const originalFetch=globalThis.fetch.bind(globalThis);
const disciplina={id:7,nome:'Estatística',descricao:'Probabilidade, análise de dados e conceitos para compreender o mundo.',possuiProva:true,periodoId:3};
const fontes=[{referencia:'F1',arquivo:'Aula 1 — Fundamentos de probabilidade.pdf',pagina:12}];
const resumo={id:'visual-1',titulo:'Como funciona a probabilidade condicional?',disciplinaId:7,assuntoId:null,atualizadoEm:new Date().toISOString()};
const salvas=[{id:1,papel:'USUARIO',conteudo:'Como funciona a probabilidade condicional?',fontes:[],criadoEm:new Date().toISOString()},{id:2,papel:'MONITOR',conteudo:'A **probabilidade condicional** representa a chance de um evento ocorrer quando já sabemos que outro evento aconteceu. [F1]\n\nA expressão é P(A | B) = P(A ∩ B) / P(B), para P(B) > 0. [F1]',fontes,criadoEm:new Date().toISOString()}];
let avaliacao=null;
globalThis.fetch=async(input,options={})=>{
 const url=new URL(typeof input==='string'?input:input.url,location.href),path=url.pathname;
 if(!path.startsWith('/api/'))return originalFetch(input,options);
 const json=data=>Promise.resolve(new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}}));
 if(path==='/api/v1/auth/me')return json({id:99,nome:'Mariana Oliveira',perfil:'ESTUDANTE'});
 if(path==='/api/v1/auth/csrf')return json({headerName:'X-CSRF-TOKEN',token:'visual-fixture'});
 if(path==='/api/v1/avaliacao-plataforma/minha'){
  if(options.method==='PUT'){const entrada=JSON.parse(options.body);avaliacao={nota:entrada.nota,comentario:entrada.comentario,enviadoEm:new Date().toISOString()};}
  return avaliacao?json(avaliacao):new Response(null,{status:204});
 }
 if(path==='/api/v1/auth/logout')return new Response(null,{status:204});
 if(path==='/api/v1/periodos')return json([{id:3,numero:3,nome:'3º período'},{id:4,numero:4,nome:'4º período'}]);
 if(path.includes('/periodos/'))return json([disciplina,{id:8,nome:'Estrutura de Dados Avançada',descricao:'Árvores, estruturas e algoritmos para organizar suas ideias.',possuiProva:false,periodoId:3},{id:9,nome:'Design de Artefatos Digitais',descricao:'Conceitos, processos e experiências que aproximam pessoas.',possuiProva:false,periodoId:3}]);
 if(path.endsWith('/assuntos'))return json([{id:11,nome:'Fundamentos de probabilidade',ordem:1},{id:12,nome:'Probabilidade condicional e independência',ordem:2},{id:13,nome:'Estimação e intervalos para a média',ordem:3}]);
 if(path.endsWith('/materiais'))return json([{id:1,titulo:'Aula 1 — Fundamentos de probabilidade',tipo:'SLIDE_AULA',fonteMonitorVirtual:true},{id:2,titulo:'Lista de exercícios — Probabilidade',tipo:'LISTA_EXERCICIOS',disponivelParaPratica:true},{id:3,titulo:'Prova anterior de Estatística',tipo:'PROVA_ANTIGA',disponivelParaPratica:true}]);
 if(path==='/api/v1/monitor/conversas')return json([resumo]);
 if(path.startsWith('/api/v1/monitor/conversas/'))return json({conversa:resumo,mensagens:salvas});
 if(path==='/api/v1/monitor/chat'){
  const entrada=JSON.parse(options.body);const resposta='Vamos conectar os conceitos! A probabilidade varia entre 0 e 1 e expressa a chance de um evento ocorrer. [F1]';
  salvas.push({id:salvas.length+1,papel:'USUARIO',conteudo:entrada.pergunta,fontes:[],criadoEm:new Date().toISOString()},{id:salvas.length+2,papel:'MONITOR',conteudo:resposta,fontes,criadoEm:new Date().toISOString()});
  return new Response([['token',{texto:resposta}],['sources',{fontes}],['done',{threadId:resumo.id}]].map(([event,data])=>`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`).join(''),{headers:{'Content-Type':'text/event-stream'}});
 }
 if(path==='/api/v1/pratica/sessoes')return json({sessaoId:'visual-pratica',questoes:[{id:'visual-q1',enunciado:'Em uma urna há **3 bolas azuis e 2 bolas verdes**. Ao retirar uma bola ao acaso, qual é a probabilidade de ela ser azul?',alternativas:{A:'1/5',B:'2/5',C:'3/5',D:'4/5',E:'1'},origem:'GERADA_IA',fontes}],estado:'DISPONIVEL'});
 if(path.includes('/respostas'))return json({correto:true,alternativaCorreta:'C',conceito:'Probabilidade clássica',formula:'P(A) = casos favoráveis / casos possíveis',substituicao:'P(azul) = 3 / 5',calculos:['Total de bolas: 3 + 2 = 5','Bolas azuis: 3','Probabilidade: 3/5 = 0,6 = 60%'],resolucao:'A chance de retirar uma bola azul é de 60%.',errosComuns:['Usar apenas as bolas verdes como total.'],dica:'Conte todos os resultados possíveis antes de dividir.',fontes});
 return new Response(JSON.stringify({mensagem:'Rota não prevista nesta validação visual.'}),{status:404});
};
await import('/src/main.jsx');
