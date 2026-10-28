import React from 'react';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {describe,it,expect,vi,beforeEach} from 'vitest';
import Avaliacao from './Avaliacao.jsx';
import {requisitar} from '../api.js';
vi.mock('../api.js',()=>({requisitar:vi.fn()}));
beforeEach(()=>vi.resetAllMocks());
describe('Avaliação da plataforma',()=>{
 it('exige nota e envia a avaliação com comentário opcional',async()=>{
  requisitar.mockResolvedValueOnce(null).mockResolvedValueOnce({nota:5,comentario:null});render(<Avaliacao/>);
  const enviar=await screen.findByRole('button',{name:'Enviar avaliação'});expect(enviar).toBeDisabled();
  fireEvent.click(screen.getByRole('radio',{name:'5 estrelas — Excelente'}));fireEvent.click(enviar);
  expect(await screen.findByText('Obrigado pela sua avaliação!')).toBeVisible();
  expect(requisitar).toHaveBeenLastCalledWith('/api/v1/avaliacao-plataforma/minha',expect.objectContaining({method:'PUT',body:{nota:5,comentario:''}}));
 });
 it('reabre a avaliação e permite atualizar a nota sem perder o comentário',async()=>{
  requisitar.mockResolvedValueOnce({nota:3,comentario:'Quero mais exemplos.'}).mockResolvedValueOnce({nota:4,comentario:'Quero mais exemplos.'});render(<Avaliacao/>);
  const atualizar=await screen.findByRole('button',{name:'Atualizar avaliação'});expect(atualizar).toBeDisabled();
  expect(screen.getByRole('radio',{name:'3 estrelas — Regular'})).toBeChecked();expect(screen.getByRole('textbox')).toHaveValue('Quero mais exemplos.');
  fireEvent.click(screen.getByRole('radio',{name:'4 estrelas — Boa'}));fireEvent.click(atualizar);
  expect(await screen.findByText('Obrigado pela sua avaliação!')).toBeVisible();
  expect(requisitar).toHaveBeenLastCalledWith('/api/v1/avaliacao-plataforma/minha',expect.objectContaining({body:{nota:4,comentario:'Quero mais exemplos.'}}));
 });
 it('preserva a nota e o comentário quando o envio falha',async()=>{
  requisitar.mockResolvedValueOnce(null).mockRejectedValueOnce(new Error('Não foi possível salvar.'));render(<Avaliacao/>);await screen.findByRole('button',{name:'Enviar avaliação'});
  fireEvent.click(screen.getByRole('radio',{name:'2 estrelas — Ruim'}));fireEvent.change(screen.getByRole('textbox'),{target:{value:'Preciso de mais clareza.'}});fireEvent.click(screen.getByRole('button',{name:'Enviar avaliação'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível salvar.');expect(screen.getByRole('textbox')).toHaveValue('Preciso de mais clareza.');expect(screen.getByRole('radio',{name:'2 estrelas — Ruim'})).toBeChecked();
 });
 it('permite tentar carregar novamente em caso de falha inicial',async()=>{
  requisitar.mockRejectedValueOnce(new Error('Falha')).mockResolvedValueOnce({nota:4,comentario:'Minha opinião'});render(<Avaliacao/>);
  fireEvent.click(await screen.findByRole('button',{name:'Tentar novamente'}));await waitFor(()=>expect(screen.getByRole('textbox')).toHaveValue('Minha opinião'));
 });
});
