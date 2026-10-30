import React from 'react';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import App from './App.jsx';
import {requisitar,conversar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));

it('seleciona Design, filtra o assunto e conversa com fontes e histórico pela API',async()=>{
 requisitar.mockImplementation(async(url)=>{
  if(url.endsWith('/auth/me'))return {id:1,nome:'Aluno Design',perfil:'ESTUDANTE'};
  if(url==='/api/v1/periodos')return [{id:23,numero:3,nome:'3º período'}];
  if(url.endsWith('/periodos/23/disciplinas'))return [{id:47,nome:'Design de Artefatos Digitais',possuiProva:false}];
  if(url.endsWith('/disciplinas/47/assuntos'))return [{id:91,nome:'Design Thinking'}];
  if(url.endsWith('/disciplinas/47/materiais'))return [{id:83,titulo:'Aula 8 — Design Thinking',tipo:'SLIDE_AULA',fonteMonitorVirtual:true,arquivoDisponivel:true,assuntoId:91}];
  return [];
 });
 conversar.mockImplementation(async(body,event)=>{
  event('token',{texto:'As etapas são empatia, definição, ideação, prototipação e teste. [F1]'});
  event('sources',{fontes:[{referencia:'F1',arquivo:'Aula 08.pdf',pagina:12,material_id:83}]});
  event('done',{threadId:'design-thread'});
 });
 render(<App/>);
 fireEvent.click(await screen.findByRole('button',{name:/Explorar materiais/}));
 expect(await screen.findByRole('option',{name:'Design de Artefatos Digitais'})).toBeInTheDocument();
 const assunto=await screen.findByRole('option',{name:'Design Thinking'});
 fireEvent.change(assunto.closest('select'),{target:{value:'91'}});
 expect(await screen.findByRole('link',{name:'Abrir Aula 8 — Design Thinking'})).toHaveAttribute('href','/api/v1/materiais/83/arquivo');
 fireEvent.click(screen.getByRole('button',{name:'Monitor Virtual'}));
 await waitFor(()=>expect(screen.getByRole('textbox')).toBeEnabled());
 fireEvent.change(screen.getByRole('textbox'),{target:{value:'Quais são as etapas do Design Thinking?'}});
 fireEvent.click(screen.getByRole('button',{name:'Enviar pergunta'}));
 expect(await screen.findByText(/As etapas são empatia/)).toBeVisible();
 expect(conversar.mock.calls[0][0]).toMatchObject({disciplinaId:47,assuntoId:91,threadId:null});
 fireEvent.click(screen.getByText('De onde veio esta explicação?'));
 expect(screen.getByRole('link',{name:/^Abrir material:/})).toHaveAttribute('href','/api/v1/materiais/83/arquivo#page=12');
 expect(requisitar).toHaveBeenCalledWith('/api/v1/monitor/conversas?disciplinaId=47&assuntoId=91',expect.any(Object));
});
