import React from 'react';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {describe,it,expect,vi,beforeEach} from 'vitest';
import {Pratica,Questao,Correcao} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>vi.clearAllMocks());
describe('Prática do estudante',()=>{
 it('respeita disciplina sem prova',()=>{render(<Pratica disciplina={{id:1,possuiProva:false}}/>);expect(screen.getByText('Prática ainda não habilitada')).toBeVisible();expect(requisitar).not.toHaveBeenCalled();});
 it('exibe estado vazio sem preencher com questões artificiais',async()=>{
  requisitar.mockResolvedValue({sessaoId:'s',estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões neste assunto.'});
  render(<Pratica disciplina={{id:1,possuiProva:true}} assuntoId={8}/>);fireEvent.click(screen.getByText('Iniciar prática'));
  expect(await screen.findByText('Nenhuma questão disponível nesta seleção')).toBeVisible();
  expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({assuntoId:8,modo:'CADASTRADAS'})}));
 });
 it('oculta a correção até o envio e apresenta os passos após responder',async()=>{
  const dados={correto:true,alternativaCorreta:'B',conceito:'Média',formula:'Σx/n',substituicao:'(2+4)/2',calculos:['Soma=6','6/2=3'],resolucao:'A média é 3.',errosComuns:['Somar sem dividir'],dica:'Conte os valores',fontes:[],aviso:'Resolução por IA'};
  requisitar.mockResolvedValue(dados);
  render(<Questao questao={{id:'q',enunciado:'Calcule a média de 2 e 4.',alternativas:{A:'2',B:'3',C:'4',D:'5',E:'6'},origem:'GERADA_IA',fontes:[]}} sessaoId="s" indice={0} total={1}/>);
  expect(screen.queryByText('Alternativa correta: B')).not.toBeInTheDocument();
  expect(screen.getByText('Conferir resposta')).toBeDisabled();fireEvent.click(screen.getByDisplayValue('B'));fireEvent.click(screen.getByText('Conferir resposta'));
  expect(await screen.findByText('Você acertou.')).toBeVisible();expect(screen.getByText('6/2=3')).toBeVisible();expect(screen.getByText('Erros comuns')).toBeVisible();
  expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes/s/respostas',{method:'POST',body:{questaoId:'q',alternativa:'B'}});
 });
});
