import React from 'react';
import {fireEvent,render,screen,waitFor} from '@testing-library/react';
import {beforeEach,expect,it,vi} from 'vitest';
import {Pratica,Correcao} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
it('envia tipo e contextualização ao backend da disciplina básica',async()=>{
 requisitar.mockResolvedValue({estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões.'});
 render(<Pratica disciplina={{id:22,nome:'Estrutura de Dados',possuiProva:true}} assuntoId={8}/>);
 expect(screen.getByLabelText('Questões')).toHaveValue('GERADAS_IA');
 expect(screen.getByText(/duas abertas ainda não foram fornecidas/)).toBeVisible();
 fireEvent.change(screen.getByLabelText('Tipo de exercício'),{target:{value:'TESTE_MESA'}});
 fireEvent.change(screen.getByLabelText('Contextualização'),{target:{value:'DETALHADO'}});
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({disciplinaId:22,assuntoId:8,tipoQuestao:'TESTE_MESA',nivelContexto:'DETALHADO',modo:'GERADAS_IA'})})));
});
it('habilita controles próprios de prática na disciplina avançada',()=>{
 render(<Pratica disciplina={{id:33,nome:'Estrutura de Dados Avançada',possuiProva:true}}/>);
 expect(screen.getByLabelText('Tipo de exercício')).toBeInTheDocument();
 expect(screen.getByLabelText('Questões')).toHaveValue('GERADAS_IA');
 expect(screen.queryByRole('option',{name:'Estilo da prova disponível'})).not.toBeInTheDocument();
});
it('renderiza código, tabela resolvida e pseudocódigo na correção',()=>{
 render(<Correcao dados={{correto:true,alternativaCorreta:'B',conceito:'Indireção',calculos:['Identifique x.','Atualize por *p.','Confira x.'],resolucao:'### Teste de mesa resolvido\n\n| Etapa | x |\n| --- | --- |\n| Final | 8 |\n\n### Pseudocódigo de apoio\n\n```text\nx <- 8\nescreva x\n```',errosComuns:[],dica:'Simule no papel.',fontes:[]}}/>);
 expect(screen.getByRole('table')).toBeVisible();
 expect(screen.getByRole('heading',{name:'Pseudocódigo de apoio'})).toBeVisible();
 expect(screen.getByText(/escreva x/)).toBeVisible();
});
