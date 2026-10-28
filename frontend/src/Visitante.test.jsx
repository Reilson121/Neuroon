import React from 'react';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import App from './App.jsx';
import {requisitar,renovarCsrf} from './api.js';

vi.mock('./api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));

it('permite explorar materiais e Monitor sem conta, sem mostrar funções restritas',async()=>{
 requisitar.mockImplementation(async(url)=>{
  if(url==='/api/v1/auth/me')throw new Error('Sem sessão');
  if(url==='/api/v1/auth/visitante')return {id:501,nome:'Visitante',email:null,perfil:'VISITANTE'};
  if(url==='/api/v1/periodos')return [{id:23,numero:3,nome:'3º período'}];
  if(url==='/api/v1/periodos/23/disciplinas')return [{id:47,nome:'Projeto de Ideação de Software',possuiProva:false}];
  if(url==='/api/v1/disciplinas/47/assuntos')return [];
  if(url==='/api/v1/disciplinas/47/materiais')return [{id:83,titulo:'Aula de ideação',tipo:'SLIDE_AULA',fonteMonitorVirtual:true,arquivoDisponivel:true}];
  return [];
 });
 render(<App/>);
 fireEvent.click(await screen.findByRole('button',{name:'Explorar sem conta'}));
 await waitFor(()=>expect(requisitar).toHaveBeenCalledWith('/api/v1/auth/visitante',{method:'POST'}));
 expect(await screen.findByRole('heading',{name:'Visitante'})).toBeVisible();
 expect(screen.queryByRole('button',{name:'Praticar'})).not.toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Avaliar plataforma'})).not.toBeInTheDocument();
 expect(screen.queryByText('Praticar com IA')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:/Explorar materiais/}));
 expect(await screen.findByRole('link',{name:'Abrir Aula de ideação'})).toHaveAttribute('href','/api/v1/materiais/83/arquivo');
 fireEvent.click(screen.getByRole('button',{name:'Monitor Virtual',exact:true}));
 expect(await screen.findByRole('textbox')).toBeEnabled();
 expect(renovarCsrf).toHaveBeenCalled();
});
