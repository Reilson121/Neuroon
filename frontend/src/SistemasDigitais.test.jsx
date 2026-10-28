import React from 'react';
import {fireEvent,render,screen} from '@testing-library/react';
import {beforeEach,expect,it,vi} from 'vitest';
import {Pratica,Correcao} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
it('inicia Sistemas Digitais por IA usando teoria e informa a ausência da prova',async()=>{
 requisitar.mockResolvedValue({estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões.'});
 render(<Pratica disciplina={{id:91,nome:'Sistemas Digitais',possuiProva:true}} assuntoId={12}/>);
 expect(screen.getByLabelText('Questões')).toHaveValue('GERADAS_IA');
 expect(screen.getByRole('option',{name:'Materiais teóricos disponíveis'})).toBeVisible();
 expect(screen.getByText(/A lista e a prova do professor ainda não foram fornecidas/)).toBeVisible();
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 await screen.findByText('Nenhuma questão disponível nesta seleção');
 expect(requisitar.mock.calls[0][1].body).toMatchObject({disciplinaId:91,assuntoId:12,modo:'GERADAS_IA',origem:'MISTO'});
});
it('explica uma questão conceitual com passos, erros e dica sem fórmula artificial',()=>{
 render(<Correcao dados={{correto:false,alternativaCorreta:'B',conceito:'Porta AND',calculos:['Identifique as entradas.','Exija simultaneidade.','Confira a saída.'],resolucao:'As duas condições devem ser satisfeitas.',errosComuns:['Não confunda AND com OR.'],dica:'Teste as quatro combinações.',fontes:[]}}/>);
 expect(screen.getByText('Resolução passo a passo')).toBeVisible();
 expect(screen.getByText('Não confunda AND com OR.')).toBeVisible();
 expect(screen.queryByText('Fórmula')).not.toBeInTheDocument();
});
