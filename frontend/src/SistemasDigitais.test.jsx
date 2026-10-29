import React from 'react';
import {fireEvent,render,screen,waitFor,configure} from '@testing-library/react';
import {beforeEach,expect,it,vi} from 'vitest';
import App,{Pratica,Correcao} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
configure({asyncUtilTimeout:10000});
it('carrega Sistemas Digitais do segundo período e usa seus assuntos e PDFs pela API',async()=>{
 requisitar.mockImplementation(async(url)=>{
  if(url.endsWith('/auth/me'))return {id:1,nome:'Aluno Digital',perfil:'ESTUDANTE'};
  if(url==='/api/v1/periodos')return [{id:22,numero:2,nome:'2º período'},{id:33,numero:3,nome:'3º período'}];
  if(url==='/api/v1/periodos/33/disciplinas')return [{id:1,nome:'Estatística',possuiProva:true}];
  if(url==='/api/v1/periodos/22/disciplinas')return [{id:91,nome:'Sistemas Digitais',possuiProva:true,periodoId:22}];
  if(url==='/api/v1/disciplinas/91/assuntos')return [{id:12,nome:'Portas lógicas e circuitos digitais'}];
  if(url==='/api/v1/disciplinas/91/materiais')return [{id:61,titulo:'Portas lógicas e circuitos digitais',tipo:'SLIDE_AULA',fonteMonitorVirtual:true,arquivoDisponivel:true,assuntoId:12}];
  if(url==='/api/v1/pratica/sessoes')return {sessaoId:'digital',estado:'SEM_QUESTOES',questoes:[],mensagem:'Sem questões.'};
  return [];
 });
 render(<App/>);
 fireEvent.click(await screen.findByRole('button',{name:/Explorar materiais/}));
 fireEvent.change(await screen.findByLabelText('Período'),{target:{value:'22'}});
 expect(await screen.findByRole('option',{name:'Sistemas Digitais'})).toBeInTheDocument();
 await waitFor(()=>expect(screen.queryByRole('option',{name:'Estatística'})).not.toBeInTheDocument());
 fireEvent.change(await screen.findByLabelText('Assunto'),{target:{value:'12'}});
 expect(await screen.findByRole('link',{name:'Abrir Portas lógicas e circuitos digitais'})).toHaveAttribute('href','/api/v1/materiais/61/arquivo');
 fireEvent.click(screen.getAllByRole('button',{name:'Praticar'})[0]);
 expect(screen.getByLabelText('Questões')).toHaveValue('GERADAS_IA');
 fireEvent.click(screen.getByRole('button',{name:'Iniciar prática'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/pratica/sessoes',expect.objectContaining({body:expect.objectContaining({disciplinaId:91,assuntoId:12})})));
},60000);
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
