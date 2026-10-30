import React from 'react';
import {fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {beforeEach,expect,it,vi} from 'vitest';
import {Pratica} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
const design={id:47,nome:'Design de Artefatos Digitais',possuiProva:true};
const assuntos=[{id:91,nome:'Design Thinking'},{id:92,nome:'Matriz CSD'}];
const sessao={sessaoId:'s1',estado:'DISPONIVEL',questoes:[{id:'q1',enunciado:'Cenário da biblioteca: qual decisão tomar?',alternativas:{A:'Investigar',B:'Supor'},fontes:[]},{id:'q2',enunciado:'Cenário da escola: qual informação validar?',alternativas:{A:'Evidências',B:'Opiniões'},fontes:[]}]};
const correcao={correto:true,alternativaCorreta:'A',conceito:'Design',calculos:[],resolucao:'Explicação da decisão.',errosComuns:[],dica:'Observe as evidências.',fontes:[]};
function configurar(){
 render(<Pratica disciplina={design} assuntos={assuntos} assuntoId={91}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:'SIMULADO'}});
 fireEvent.click(screen.getByRole('checkbox',{name:'Matriz CSD'}));
}
it('envia teste de mesa e contexto direto para a disciplina avançada',async()=>{
 requisitar.mockResolvedValue({estado:'SEM_QUESTOES',questoes:[]});
 render(<Pratica disciplina={{id:33,nome:'Estrutura de Dados Avançada',possuiProva:true}} assuntoId={8}/>);
 expect(screen.getByLabelText('Contextualização')).toHaveValue('DETALHADO');
 fireEvent.change(screen.getByLabelText('Tipo de exercício'),{target:{value:'TESTE_MESA'}});
 fireEvent.change(screen.getByLabelText('Contextualização'),{target:{value:'DIRETO'}});
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({disciplinaId:33,assuntoId:8,modo:'GERADAS_IA',tipoQuestao:'TESTE_MESA',nivelContexto:'DIRETO'})})));
});
it('simulado seleciona conteúdos, permite revisar e só corrige ao finalizar',async()=>{
 requisitar.mockImplementation(async url=>url.endsWith('/sessoes')?sessao:correcao);
 configurar();
 fireEvent.click(screen.getByRole('button',{name:'Iniciar simulado'}));
 await screen.findByText(sessao.questoes[0].enunciado);
 expect(requisitar.mock.calls[0][1].body).toMatchObject({disciplinaId:47,assuntoId:null,assuntoIds:[91,92]});
 expect(screen.getByLabelText('Atividade')).toBeDisabled();
 const grupos=screen.getAllByRole('group').filter(g=>g.tagName==='FIELDSET'&&g.querySelector('input[type=radio]'));
 fireEvent.click(within(grupos[0]).getByRole('radio',{name:/Supor/}));
 fireEvent.click(within(grupos[0]).getByRole('radio',{name:/Investigar/}));
 expect(screen.getByRole('button',{name:'Finalizar simulado'})).toBeDisabled();
 expect(requisitar).toHaveBeenCalledTimes(1);
 expect(screen.queryByText('Explicação da decisão.')).not.toBeInTheDocument();
 fireEvent.click(within(grupos[1]).getByRole('radio',{name:/Evidências/}));
 fireEvent.click(screen.getByRole('button',{name:'Finalizar simulado'}));
 await screen.findByRole('heading',{name:'Resultado do simulado'});
 expect(screen.getByText('2 de 2 acertos · 100%')).toBeVisible();
 expect(screen.getAllByText('Explicação da decisão.')).toHaveLength(2);
 expect(requisitar.mock.calls.filter(c=>c[0].endsWith('/respostas'))).toHaveLength(2);
 expect(screen.getByLabelText('Atividade')).toBeEnabled();
});
it('exige seleção e quantidade suficiente para os conteúdos',()=>{
 render(<Pratica disciplina={design} assuntos={assuntos}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:'SIMULADO'}});
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeDisabled();
 assuntos.forEach(a=>fireEvent.click(screen.getByRole('checkbox',{name:a.nome})));
 fireEvent.change(screen.getByLabelText('Quantidade'),{target:{value:'1'}});
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeDisabled();
 expect(screen.getByRole('alert')).toHaveTextContent('igual ou maior');
});
it('mantém respostas e retoma correção parcial sem revelar resultado incompleto',async()=>{
 let falhou=false;
 requisitar.mockImplementation(async url=>{
  if(url.endsWith('/sessoes'))return sessao;
  if(url.includes('/respostas')&&!falhou){falhou=true;throw new Error('Conexão');}
  return correcao;
 });
 configurar();fireEvent.click(screen.getByRole('button',{name:'Iniciar simulado'}));
 await screen.findByText(sessao.questoes[0].enunciado);
 screen.getAllByRole('radio').filter(r=>r.value==='A').forEach(r=>fireEvent.click(r));
 fireEvent.click(screen.getByRole('button',{name:'Finalizar simulado'}));
 await screen.findByRole('alert');
 expect(screen.queryByRole('heading',{name:'Resultado do simulado'})).not.toBeInTheDocument();
 expect(screen.queryByText('Explicação da decisão.')).not.toBeInTheDocument();
 screen.getAllByRole('radio').forEach(r=>expect(r).toBeDisabled());
 fireEvent.click(screen.getByRole('button',{name:'Tentar finalizar novamente'}));
 await screen.findByRole('heading',{name:'Resultado do simulado'});
 expect(requisitar.mock.calls.filter(c=>c[0].endsWith('/respostas'))).toHaveLength(3);
});
