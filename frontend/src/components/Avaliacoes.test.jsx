import React from 'react';
import {render,screen,fireEvent} from '@testing-library/react';
import {beforeEach,it,expect,vi} from 'vitest';
import Avaliacoes from './Avaliacoes.jsx';
import {requisitar} from '../api.js';
vi.mock('../api.js',()=>({requisitar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
it('mostra resumo, nome, comentário e data no horário de Fortaleza',async()=>{
 requisitar.mockResolvedValue({total:2,media:4.5,comComentario:1,totalPaginas:1,avaliacoes:[{id:1,aluno:'Júlia',nota:4,comentario:null,enviadoEm:'2026-10-30T13:18:00'},{id:2,aluno:'Giovana',nota:5,comentario:'Gostei!',enviadoEm:'2026-10-30T13:17:00'}]});
 render(<Avaliacoes/>);
 expect(await screen.findByText('Júlia')).toBeVisible();expect(screen.getByText('4,5 / 5')).toBeVisible();
 expect(screen.getByText('Sem comentário.')).toBeVisible();expect(screen.getByText('Gostei!')).toBeVisible();
 expect(screen.getByText(/30\/10\/2026.*10:18/)).toBeVisible();
});
it('recupera falha e apresenta estado vazio',async()=>{
 requisitar.mockRejectedValueOnce(new Error('Falha na consulta')).mockResolvedValueOnce({total:0,media:null,comComentario:0,totalPaginas:0,avaliacoes:[]});
 render(<Avaliacoes/>);expect(await screen.findByRole('alert')).toHaveTextContent('Falha na consulta');
 fireEvent.click(screen.getByRole('button',{name:'Atualizar avaliações'}));expect(await screen.findByText('Nenhuma avaliação recebida')).toBeVisible();
});
it('consulta a próxima página sem mudar as estatísticas globais',async()=>{
 requisitar.mockResolvedValue({total:11,media:5,comComentario:0,totalPaginas:2,avaliacoes:[{id:1,aluno:'Aluno',nota:5,enviadoEm:'2026-10-30T13:18:00'}]});
 render(<Avaliacoes/>);fireEvent.click(await screen.findByRole('button',{name:'Próxima'}));
 expect(await screen.findByText('Página 2 de 2')).toBeVisible();expect(requisitar).toHaveBeenLastCalledWith('/api/v1/avaliacoes?pagina=1',expect.anything());
});
