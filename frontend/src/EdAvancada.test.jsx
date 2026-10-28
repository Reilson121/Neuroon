import React from 'react';
import {render,screen,fireEvent} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import App,{Materiais,Fontes} from './App.jsx';
import {requisitar} from './api.js';
vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));

it('abre PDFs e fontes citadas pela API pública',()=>{
 render(<><Materiais materiais={[{id:8,titulo:'Aula 2 — Estrutura de Dados Avançada',tipo:'SLIDE_AULA',fonteMonitorVirtual:true,arquivoDisponivel:true}]} usuario={{perfil:'ESTUDANTE'}}/><Fontes fontes={[{referencia:'F1',arquivo:'Aula_2.pdf',pagina:90,material_id:8}]}/></>);
 expect(screen.getByRole('link',{name:'Abrir Aula 2 — Estrutura de Dados Avançada'})).toHaveAttribute('href','/api/v1/materiais/8/arquivo');
 expect(screen.getByRole('link',{name:'Abrir referência F1'})).toHaveAttribute('href','/api/v1/materiais/8/arquivo#page=90');
});

it('seleciona ED no catálogo, carrega assuntos e apresenta os materiais reais da API',async()=>{
 requisitar.mockImplementation(async(url)=>{
  if(url.endsWith('/auth/me'))return {id:1,nome:'Aluno ED',perfil:'ESTUDANTE'};
  if(url==='/api/v1/periodos')return [{id:3,numero:3,nome:'3º período'}];
  if(url.endsWith('/periodos/3/disciplinas'))return [{id:42,nome:'Estrutura de Dados Avançada',possuiProva:false}];
  if(url.endsWith('/disciplinas/42/assuntos'))return [{id:9,nome:'Árvores balanceadas e AVL'}];
  if(url.endsWith('/disciplinas/42/materiais'))return [{id:8,titulo:'Aula 2',tipo:'SLIDE_AULA',arquivoDisponivel:true}];
  return [];
 });
 render(<App/>);
 fireEvent.click(await screen.findByRole('button',{name:/Explorar materiais/}));
 expect(await screen.findByRole('option',{name:'Estrutura de Dados Avançada'},{timeout:10000})).toBeInTheDocument();
 expect(await screen.findByRole('option',{name:'Árvores balanceadas e AVL'},{timeout:10000})).toBeInTheDocument();
 expect(await screen.findByRole('link',{name:'Abrir Aula 2'},{timeout:10000})).toHaveAttribute('href','/api/v1/materiais/8/arquivo');
});
