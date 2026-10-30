import React from 'react';
import {fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {beforeEach,expect,it,vi} from 'vitest';
import {Pratica} from './App.jsx';
import {requisitar} from './api.js';
import topicos from './calculo-topicos.json';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
const disciplina={id:23,nome:'Cálculo para Computação I',possuiProva:true};
it('envia unidade, regra e função e abre a tabela de apoio',async()=>{
 requisitar.mockResolvedValue({estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões.'});
 render(<Pratica disciplina={disciplina} materiais={[{id:101,titulo:'Tabela de Derivadas do Prof. Douglas Maioli',arquivoDisponivel:true}]}/>);
 expect(screen.getByLabelText('Questões')).toHaveValue('GERADAS_IA');
 expect(screen.getByRole('link',{name:'Abrir tabela de derivadas'})).toHaveAttribute('href','/api/v1/materiais/101/arquivo');
 fireEvent.change(screen.getByLabelText('Unidade'),{target:{value:'2'}});
 fireEvent.change(screen.getByLabelText('Tópico ou regra'),{target:{value:'cadeia'}});
 fireEvent.change(screen.getByLabelText('Tipo de função'),{target:{value:'TRIGONOMETRICA'}});
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({disciplinaId:23,unidadeCalculo:2,topicoCalculo:'cadeia',tipoFuncao:'TRIGONOMETRICA'})})));
});
it('primeira unidade não oferece derivadas e a mudança limpa os filtros',()=>{
 render(<Pratica disciplina={disciplina}/>);
 fireEvent.change(screen.getByLabelText('Unidade'),{target:{value:'2'}});
 fireEvent.change(screen.getByLabelText('Tópico ou regra'),{target:{value:'cadeia'}});
 fireEvent.change(screen.getByLabelText('Tipo de função'),{target:{value:'RADICAL'}});
 fireEvent.change(screen.getByLabelText('Unidade'),{target:{value:'1'}});
 expect(within(screen.getByLabelText('Tópico ou regra')).queryByRole('option',{name:'Regra da cadeia'})).not.toBeInTheDocument();
 expect(screen.getByLabelText('Tópico ou regra')).toHaveValue('MISTO');
 expect(screen.getByLabelText('Tipo de função')).toHaveValue('MISTO');
});
it('restringe tópicos ao assunto e informa a ausência da prova 2',()=>{
 render(<Pratica disciplina={disciplina} assuntoId={77} assuntos={[{id:77,ordem:4}]}/>);
 expect(within(screen.getByLabelText('Tópico ou regra')).queryByRole('option',{name:'Composição de funções'})).not.toBeInTheDocument();
 expect(within(screen.getByLabelText('Tópico ou regra')).getByRole('option',{name:'Limites por substituição'})).toBeVisible();
 expect(screen.getByText(/A prova da 2ª unidade ainda não foi fornecida/)).toBeVisible();
});
it('esconde a prática anterior ao mudar o tipo de função',async()=>{
 requisitar.mockResolvedValue({estado:'DISPONIVEL',sessaoId:'s1',questoes:[{id:'q1',enunciado:'Calcule a questão anterior.',alternativas:{A:'1',B:'2'},fontes:[]}]});
 render(<Pratica disciplina={disciplina}/>);
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 expect(await screen.findByText('Calcule a questão anterior.')).toBeVisible();
 fireEvent.change(screen.getByLabelText('Tipo de função'),{target:{value:'RADICAL'}});
 expect(screen.queryByText('Calcule a questão anterior.')).not.toBeInTheDocument();
});

const assuntos=Array.from({length:9},(_,i)=>({id:101+i,ordem:i+1,nome:topicos.find(t=>t.assuntoOrdem===i+1).assunto}));
it.each([['UNIDADE_1',[101,102,103,104,105],1],['UNIDADE_2',[106,107,108,109],2],['FINAL',assuntos.map(a=>a.id),0],['SEGUNDA_CHAMADA',assuntos.map(a=>a.id),0]])('monta %s com todos os assuntos previstos, independentemente do filtro superior',async(tipo,ids,unidade)=>{
 requisitar.mockResolvedValue({estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões.'});
 render(<Pratica disciplina={disciplina} assuntoId={101} assuntos={assuntos}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:tipo}});
 fireEvent.click(screen.getByRole('button',{name:'Iniciar simulado'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({assuntoId:null,assuntoIds:ids,quantidade:10,unidadeCalculo:unidade,topicoCalculo:'MISTO',tipoFuncao:'MISTO',origem:'MISTO',modo:'GERADAS_IA'})})));
});
it('exige assuntos e quantidade suficiente no simulado personalizado',()=>{
 render(<Pratica disciplina={disciplina} assuntos={assuntos}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:'ASSUNTOS'}});
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeDisabled();
 fireEvent.click(screen.getByRole('checkbox',{name:assuntos[0].nome}));
 fireEvent.click(screen.getByRole('checkbox',{name:assuntos[5].nome}));
 fireEvent.change(screen.getByLabelText('Quantidade de questões'),{target:{value:'1'}});
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeDisabled();
 fireEvent.change(screen.getByLabelText('Quantidade de questões'),{target:{value:'3'}});
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeEnabled();
});
it('bloqueia prova de unidade quando o catálogo está incompleto',()=>{
 render(<Pratica disciplina={disciplina} assuntos={assuntos.slice(0,2)}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:'UNIDADE_1'}});
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeDisabled();
 expect(screen.getByRole('alert')).toHaveTextContent('catálogo está incompleto');
});
it('corrige a prova de Cálculo somente na entrega e permite uma nova segunda chamada',async()=>{
 const q={id:'q1',enunciado:'Calcule a derivada de x².',alternativas:{A:'2x',B:'x'},fontes:[]};
 requisitar.mockImplementation(async url=>url.endsWith('/sessoes')?{estado:'DISPONIVEL',sessaoId:'s1',questoes:[q]}:{correto:true,alternativaCorreta:'A',conceito:'Derivada',resolucao:'A derivada é 2x.',fontes:[]});
 render(<Pratica disciplina={disciplina} assuntos={assuntos}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:'FINAL'}});
 fireEvent.click(screen.getByRole('button',{name:'Iniciar simulado'}));
 await screen.findByText(q.enunciado);
 expect(screen.getByLabelText('Atividade')).toBeDisabled();
 fireEvent.click(screen.getByRole('radio',{name:/2x/}));
 expect(requisitar).toHaveBeenCalledTimes(1);
 expect(screen.queryByText('A derivada é 2x.')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Finalizar simulado'}));
 await screen.findByRole('heading',{name:'Resultado do simulado'});
 expect(screen.getByText('1 de 1 acertos · 100%')).toBeVisible();
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:'SEGUNDA_CHAMADA'}});
 expect(screen.queryByRole('heading',{name:'Resultado do simulado'})).not.toBeInTheDocument();
 expect(screen.getByRole('button',{name:'Iniciar simulado'})).toBeEnabled();
});
it('a referência da UP1 só oferece tópicos e tipos presentes nessa prova',()=>{
 render(<Pratica disciplina={disciplina}/>);
 fireEvent.change(screen.getByLabelText('Unidade'),{target:{value:'2'}});
 fireEvent.change(screen.getByLabelText('Referência'),{target:{value:'PROVA'}});
 expect(screen.getByLabelText('Unidade')).toHaveValue('0');
 expect(within(screen.getByLabelText('Unidade')).queryByRole('option',{name:/2ª unidade/})).not.toBeInTheDocument();
 expect(within(screen.getByLabelText('Tópico ou regra')).queryByRole('option',{name:'Regra da cadeia'})).not.toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('Tópico ou regra'),{target:{value:'inversa'}});
 expect(within(screen.getByLabelText('Tipo de função')).queryByRole('option',{name:'Exponencial'})).not.toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('Referência'),{target:{value:'MISTO'}});
 fireEvent.change(screen.getByLabelText('Tópico ou regra'),{target:{value:'inversa'}});
 expect(within(screen.getByLabelText('Tipo de função')).getByRole('option',{name:'Exponencial'})).toBeVisible();
});
