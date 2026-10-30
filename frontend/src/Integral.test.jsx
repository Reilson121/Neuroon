import React from 'react';
import {fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {beforeEach,expect,it,vi} from 'vitest';
import {Pratica} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>{vi.resetAllMocks();requisitar.mockResolvedValue({estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões.'});});
const disciplina={id:30,nome:'Cálculo para Computação II',possuiProva:true};
const assuntos=Array.from({length:8},(_,i)=>({id:i+1,ordem:i+1,nome:i===7?'Complemento opcional':`Assunto ${i+1}`}));
it('oferece tabela de integrais e filtra primeira unidade sem duplas ou derivadas',async()=>{
 render(<Pratica disciplina={disciplina} assuntos={assuntos} materiais={[{id:301,titulo:'Tabela de Integrais - apoio NEURON',arquivoDisponivel:true}]}/>);
 expect(screen.getByRole('link',{name:'Abrir tabela de integrais'})).toHaveAttribute('href','/api/v1/materiais/301/arquivo');
 expect(screen.queryByRole('option',{name:'Provas anteriores'})).not.toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('Unidade'),{target:{value:'1'}});
 const regras=within(screen.getByLabelText('Tópico ou regra'));
 expect(regras.queryByRole('option',{name:/Integral dupla/})).not.toBeInTheDocument();
 expect(regras.getByRole('option',{name:'Integral definida e F(b) - F(a)'})).toBeVisible();
 fireEvent.change(screen.getByLabelText('Tópico ou regra'),{target:{value:'integral_definida'}});
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({disciplinaId:30,unidadeCalculo:1,topicoCalculo:'integral_definida'})})));
});
it.each([['UNIDADE_1',[1,2,3]],['UNIDADE_2',[4,5,6,7]],['FINAL',[1,2,3,4,5,6,7]],['SEGUNDA_CHAMADA',[1,2,3,4,5,6,7]]])('simulado %s exclui complemento',async(tipo,ids)=>{
 render(<Pratica disciplina={disciplina} assuntos={assuntos}/>);
 fireEvent.change(screen.getByLabelText('Atividade'),{target:{value:tipo}});
 expect(screen.getByText(/esta disciplina não tem prova oficial/i)).toBeVisible();
 expect(screen.queryByText('Complemento opcional')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Iniciar simulado'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({assuntoIds:ids})})));
});
