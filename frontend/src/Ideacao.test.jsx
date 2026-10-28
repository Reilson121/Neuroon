import React from 'react';
import {render,screen,fireEvent,waitFor,configure} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import App from './App.jsx';
import {requisitar,conversar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
configure({asyncUtilTimeout:10000});

it('seleciona Ideação, filtra o assunto e conversa com fontes e histórico pela API',async()=>{
 requisitar.mockImplementation(async(url)=>{
  if(url.endsWith('/auth/me'))return {id:1,nome:'Aluno Ideação',perfil:'ESTUDANTE'};
  if(url==='/api/v1/periodos')return [{id:23,numero:3,nome:'3º período'}];
  if(url.endsWith('/periodos/23/disciplinas'))return [{id:47,nome:'Projeto de Ideação de Software',possuiProva:false}];
  if(url.endsWith('/disciplinas/47/assuntos'))return [{id:90,nome:'Introdução'},{id:91,nome:'Lean Canvas'},{id:92,nome:'Histórias de Usuário'},{id:93,nome:'Mapa de Navegação e Wireframe'},{id:94,nome:'Matriz CSD'}];
  if(url.endsWith('/disciplinas/47/materiais'))return [{id:82,titulo:'Aula 1 — Introdução',tipo:'SLIDE_AULA',fonteMonitorVirtual:true,arquivoDisponivel:true,assuntoId:90},{id:83,titulo:'Aula 2 — Lean Canvas',tipo:'SLIDE_AULA',fonteMonitorVirtual:true,arquivoDisponivel:true,assuntoId:91}];
  return [];
 });
 conversar.mockImplementation(async(body,event)=>{
  event('token',{texto:'O Lean Canvas organiza a proposta de negócio em nove blocos. [F1]'});
  event('sources',{fontes:[{referencia:'F1',arquivo:'Aula 02- Projeto de Ideao de Software - LEAN CANVAS.pdf',pagina:12,material_id:83}]});
  event('done',{threadId:'ideacao-thread'});
 });
 render(<App/>);
 fireEvent.click(await screen.findByRole('button',{name:/Explorar materiais/}));
 expect(await screen.findByRole('option',{name:'Projeto de Ideação de Software'})).toBeInTheDocument();
 const assunto=await screen.findByRole('option',{name:'Lean Canvas'});
 fireEvent.change(assunto.closest('select'),{target:{value:'91'}});
 expect(await screen.findByRole('link',{name:'Abrir Aula 2 — Lean Canvas'})).toHaveAttribute('href','/api/v1/materiais/83/arquivo');
 expect(screen.queryByRole('link',{name:'Abrir Aula 1 — Introdução'})).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Monitor Virtual'}));
 await waitFor(()=>expect(screen.getByRole('textbox')).toBeEnabled());
 fireEvent.change(screen.getByRole('textbox'),{target:{value:'Quais são os blocos do Lean Canvas?'}});
 fireEvent.click(screen.getByRole('button',{name:'Enviar pergunta'}));
 expect(await screen.findByText(/O Lean Canvas organiza/)).toBeVisible();
 expect(conversar.mock.calls[0][0]).toMatchObject({disciplinaId:47,assuntoId:91,threadId:null});
 fireEvent.click(screen.getByText('1 fonte consultada'));
 expect(screen.getByRole('link',{name:'Abrir referência F1'})).toHaveAttribute('href','/api/v1/materiais/83/arquivo#page=12');
 expect(requisitar).toHaveBeenCalledWith('/api/v1/monitor/conversas?disciplinaId=47&assuntoId=91',expect.any(Object));
 fireEvent.click(screen.getAllByRole('button',{name:'Praticar'})[0]);
 expect(await screen.findByText('Prática ainda não habilitada')).toBeVisible();
 expect(screen.queryByRole('button',{name:'Iniciar prática'})).not.toBeInTheDocument();
},60000);
