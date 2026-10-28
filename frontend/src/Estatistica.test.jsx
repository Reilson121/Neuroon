import React from 'react';
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {beforeEach,describe,expect,it,vi} from 'vitest';
import {Pratica} from './App.jsx';
import {requisitar} from './api.js';

vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
const disciplina={id:41,possuiProva:true};
const vazia={estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões autorizadas para esta seleção.'};
const disponivel={sessaoId:'sessao-original',estado:'DISPONIVEL',questoes:[{id:'q1',enunciado:'Enunciado anterior',alternativas:{A:'1',B:'2',C:'3',D:'4',E:'5'},origem:'MATERIAL_ACADEMICO',fontes:[]}]};
beforeEach(()=>vi.resetAllMocks());

describe('Integração da seleção de prática de Estatística',()=>{
 it('envia os filtros escolhidos para a API pública sem presumir IDs fixos',async()=>{
  requisitar.mockResolvedValue(vazia);
  render(<Pratica disciplina={disciplina} assuntoId={73}/>);
  fireEvent.change(screen.getByLabelText('Questões'),{target:{value:'GERADAS_IA'}});
  fireEvent.change(screen.getByLabelText('Referência'),{target:{value:'PROVA'}});
  fireEvent.change(screen.getByLabelText('Quantidade'),{target:{value:'3'}});
  fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
  expect(await screen.findByText('Nenhuma questão disponível nesta seleção')).toBeVisible();
  expect(requisitar).toHaveBeenCalledExactlyOnceWith('/api/v1/pratica/sessoes',{
   method:'POST',signal:expect.any(AbortSignal),
   body:{disciplinaId:41,assuntoId:73,modo:'GERADAS_IA',origem:'PROVA',quantidade:3,revisarVistas:false},
  });
 });

 it('aborta a requisição e ignora sua resposta se o assunto mudar',async()=>{
  let concluir;
  requisitar.mockImplementation(()=>new Promise(resolve=>{concluir=resolve;}));
  const {rerender}=render(<Pratica disciplina={disciplina} assuntoId={73}/>);
  fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
  const signal=requisitar.mock.calls[0][1].signal;
  expect(screen.getByLabelText('Questões')).toBeDisabled();
  expect(screen.getByLabelText('Referência')).toBeDisabled();
  expect(screen.getByLabelText('Quantidade')).toBeDisabled();
  rerender(<Pratica disciplina={disciplina} assuntoId={74}/>);
  expect(signal.aborted).toBe(true);
  await act(async()=>concluir(disponivel));
  expect(screen.queryByText('Enunciado anterior')).not.toBeInTheDocument();
  expect(screen.getByRole('button',{name:'Iniciar prática'})).toBeEnabled();
 });

 it('limpa questões ao trocar o modo e só revisa vistas após escolha explícita',async()=>{
  requisitar.mockResolvedValueOnce(disponivel).mockResolvedValue(vazia);
  render(<Pratica disciplina={disciplina} assuntoId={73}/>);
  fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
  expect(await screen.findByText('Enunciado anterior')).toBeVisible();
  fireEvent.change(screen.getByLabelText('Questões'),{target:{value:'GERADAS_IA'}});
  expect(screen.queryByText('Enunciado anterior')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
  fireEvent.click(await screen.findByRole('button',{name:'Revisar questões já vistas'}));
  await waitFor(()=>expect(requisitar).toHaveBeenCalledTimes(3));
  expect(requisitar.mock.calls[1][1].body).toMatchObject({modo:'GERADAS_IA',revisarVistas:false});
  expect(requisitar.mock.calls[2][1].body).toMatchObject({modo:'GERADAS_IA',revisarVistas:true});
  await screen.findByText('Nenhuma questão disponível nesta seleção');
 });

 it('exibe indisponibilidade do serviço e permite nova tentativa sem inventar questões',async()=>{
  requisitar.mockRejectedValue(new Error('Não foi possível preparar a prática. Tente novamente.'));
  render(<Pratica disciplina={disciplina} assuntoId={73}/>);
  fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível preparar a prática. Tente novamente.');
  expect(screen.getByRole('button',{name:'Iniciar prática'})).toBeEnabled();
  expect(screen.queryByRole('radio')).not.toBeInTheDocument();
 });
});
