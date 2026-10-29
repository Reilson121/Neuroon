import React from 'react';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {beforeEach,it,expect,vi} from 'vitest';
import Usuarios from './Usuarios.jsx';
import {Login} from '../App.jsx';
import {requisitar} from '../api.js';
vi.mock('../api.js',()=>({requisitar:vi.fn(),renovarCsrf:vi.fn(),conversar:vi.fn()}));
const ana={id:2,nome:'Ana',email:'ana@example.test',perfil:'ESTUDANTE'};
beforeEach(()=>{vi.resetAllMocks();requisitar.mockResolvedValue({usuarios:[ana],total:1,totalPaginas:1,pagina:0});});
it('cadastra pela tela de entrada e orienta o login',async()=>{
 render(<Login onLogin={vi.fn()}/>);fireEvent.click(screen.getByText('Criar uma conta'));
 fireEvent.change(screen.getByLabelText('Nome completo'),{target:{value:'Ana'}});
 fireEvent.change(screen.getByLabelText('Email'),{target:{value:'ana@example.test'}});
 fireEvent.change(screen.getByLabelText('Senha'),{target:{value:'senha-segura-123'}});
 fireEvent.click(screen.getByRole('button',{name:/Criar conta/}));
 expect(await screen.findByText('Conta criada! Entre com seu email e senha.')).toBeVisible();
 expect(requisitar).toHaveBeenCalledWith('/api/v1/auth/cadastro',{method:'POST',body:{nome:'Ana',email:'ana@example.test',senha:'senha-segura-123'}});
});
it('cria e atualiza a lista',async()=>{
 render(<Usuarios/>);await screen.findByText('Ana');fireEvent.click(screen.getByText('Novo usuário'));
 fireEvent.change(screen.getByLabelText('Nome completo'),{target:{value:'Bia'}});
 fireEvent.change(screen.getByLabelText('Email'),{target:{value:'bia@example.test'}});
 fireEvent.change(screen.getByLabelText('Senha'),{target:{value:'senha-segura-123'}});fireEvent.click(screen.getByText('Salvar usuário'));
 expect(await screen.findByText('Usuário cadastrado.')).toBeVisible();
 expect(requisitar).toHaveBeenCalledWith('/api/v1/admin/usuarios',{method:'POST',body:{nome:'Bia',email:'bia@example.test',senha:'senha-segura-123'}});
});
it('edita sem exigir a troca de senha',async()=>{
 requisitar.mockImplementation(path=>Promise.resolve(path.endsWith('/2')?ana:{usuarios:[ana],total:1,totalPaginas:1}));
 render(<Usuarios/>);fireEvent.click(await screen.findByLabelText('Editar Ana'));
 fireEvent.change(await screen.findByLabelText('Nome completo'),{target:{value:'Ana Souza'}});fireEvent.click(screen.getByText('Salvar usuário'));
 expect(await screen.findByText('Usuário atualizado.')).toBeVisible();
 expect(requisitar).toHaveBeenCalledWith('/api/v1/admin/usuarios/2',{method:'PUT',body:{nome:'Ana Souza',email:'ana@example.test',senha:''}});
});
it('pede confirmação de exclusão e exibe falhas sem esconder a lista',async()=>{
 render(<Usuarios/>);fireEvent.click(await screen.findByLabelText('Excluir Ana'));
 expect(requisitar).not.toHaveBeenCalledWith('/api/v1/admin/usuarios/2',{method:'DELETE'});
 fireEvent.click(screen.getByText('Cancelar exclusão'));expect(screen.queryByText('Confirmar exclusão')).not.toBeInTheDocument();
 fireEvent.click(screen.getByLabelText('Excluir Ana'));requisitar.mockRejectedValueOnce(new Error('Não foi possível excluir.'));
 fireEvent.click(screen.getByText('Confirmar exclusão'));
 expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível excluir.');expect(screen.getByText('Ana')).toBeVisible();
 fireEvent.click(screen.getByText('Confirmar exclusão'));
 await waitFor(()=>expect(screen.queryByText('Confirmar exclusão')).not.toBeInTheDocument());
 expect(requisitar).toHaveBeenCalledWith('/api/v1/admin/usuarios/2',{method:'DELETE'});
});
