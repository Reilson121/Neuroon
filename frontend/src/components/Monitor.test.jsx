import React from 'react';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {beforeEach,describe,expect,it,vi} from 'vitest';
import Monitor from './Monitor.jsx';
import {requisitar,conversar} from '../api.js';
vi.mock('../api.js',()=>({requisitar:vi.fn(),conversar:vi.fn()}));
const props={disciplina:{id:7,nome:'Estatística'},assuntoId:null,Fontes:({fontes})=><span>{fontes.map(f=>f.arquivo).join(', ')}</span>};
const resumo={id:'c1',titulo:'Explique probabilidade',disciplinaId:7,assuntoId:null,atualizadoEm:'2026-10-28T12:00:00Z'};
beforeEach(()=>vi.resetAllMocks());
async function pronto(){await waitFor(()=>expect(screen.getByRole('textbox')).toBeEnabled());}
async function enviar(texto){fireEvent.change(screen.getByRole('textbox'),{target:{value:texto}});fireEvent.click(screen.getByRole('button',{name:'Enviar pergunta'}));await waitFor(()=>expect(screen.getByRole('textbox')).toBeEnabled());}
describe('Histórico do Monitor Virtual',()=>{
 it('exibe esquemas e tabelas da explicação com as fontes e mantém a continuação',async()=>{
  requisitar.mockResolvedValue([]);
  conversar.mockImplementation(async(body,event)=>{
   event('token',{texto:'Exemplo didático criado pela IA. [F1]\n\n```text\nTOPO -> C\n        B\n        A\n```\n\n| Ação | Resultado |\n| --- | --- |\n| Retirar | C |\n\n[F1]'});
   event('sources',{fontes:[{arquivo:'Aula_0.pdf',pagina:14}]});event('done',{threadId:'c1'});
  });
  render(<Monitor {...props}/>);await pronto();await enviar('Pode explicar de forma mais didática e visual?');
  expect(screen.getByText(/TOPO -> C/).closest('pre')).toBeVisible();
  expect(screen.getByRole('table')).toBeVisible();
  fireEvent.click(screen.getByText('De onde veio esta explicação?'));expect(screen.getByText('Aula_0.pdf')).toBeVisible();
  await enviar('Agora outro exemplo');expect(conversar.mock.calls[1][0].threadId).toBe('c1');
 });
 it('mantém várias perguntas e continua usando a conversa salva',async()=>{
  requisitar.mockResolvedValue([]);let chamada=0;
  conversar.mockImplementation(async(body,event)=>{chamada++;event('token',{texto:`Explicação ${chamada}`});event('sources',{fontes:[{arquivo:'Aula.pdf'}]});event('done',{threadId:'c1'});});
  render(<Monitor {...props}/>);await pronto();await enviar('Primeira dúvida');await enviar('Segunda dúvida');
  expect(screen.getByText('Primeira dúvida')).toBeVisible();expect(screen.getByText('Explicação 1')).toBeVisible();expect(screen.getByText('Segunda dúvida')).toBeVisible();expect(screen.getByText('Explicação 2')).toBeVisible();
  expect(conversar.mock.calls[1][0]).toMatchObject({threadId:'c1',disciplinaId:7});
 });
 it('reabre perguntas, respostas e fontes após sair e voltar ao Monitor',async()=>{
  requisitar.mockImplementation(async(path)=>path.includes('/conversas/c1')?{conversa:resumo,mensagens:[{id:1,papel:'USUARIO',conteudo:'Pergunta salva'},{id:2,papel:'MONITOR',conteudo:'Resposta salva',fontes:[{arquivo:'Aula 1.pdf'}]}]}:[resumo]);
  const primeira=render(<Monitor {...props}/>);await pronto();primeira.unmount();render(<Monitor {...props}/>);await pronto();
  fireEvent.click(screen.getByRole('button',{name:/Explique probabilidade/}));
  expect(await screen.findByText('Resposta salva')).toBeVisible();expect(screen.getByText('Pergunta salva')).toBeVisible();
  fireEvent.click(screen.getByText('De onde veio esta explicação?'));expect(screen.getByText('Aula 1.pdf')).toBeVisible();
  fireEvent.click(screen.getByRole('button',{name:'Nova conversa'}));expect(screen.queryByText('Resposta salva')).not.toBeInTheDocument();expect(screen.getByRole('button',{name:/Explique probabilidade/})).toBeVisible();
 });
 it('recupera a pergunta quando o envio falha sem manter resposta incompleta',async()=>{
  requisitar.mockResolvedValue([]);conversar.mockImplementation(async(body,event)=>{event('token',{texto:'Texto parcial'});throw new Error('Serviço indisponível');});
  render(<Monitor {...props}/>);await pronto();await enviar('Minha dúvida');
  expect(screen.getByRole('alert')).toHaveTextContent('Serviço indisponível');expect(screen.getByRole('textbox')).toHaveValue('Minha dúvida');expect(screen.queryByText('Texto parcial')).not.toBeInTheDocument();
 });
 it('abre e fecha o histórico pelo controle para celular e pela tecla Escape',async()=>{
  requisitar.mockResolvedValue([]);render(<Monitor {...props}/>);await pronto();
  fireEvent.click(screen.getByRole('button',{name:'Abrir histórico'}));expect(screen.getByLabelText('Histórico do Monitor Virtual').parentElement).toHaveClass('history-open');
  fireEvent.keyDown(screen.getByRole('button',{name:'Fechar histórico'}),{key:'Escape'});expect(screen.getByLabelText('Histórico do Monitor Virtual').parentElement).not.toHaveClass('history-open');
 });
});
