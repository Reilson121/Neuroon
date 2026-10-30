import React from 'react';
import {render,screen,fireEvent} from '@testing-library/react';
import {describe,expect,it} from 'vitest';
import RespostaMonitor from './RespostaMonitor.jsx';

const fontes=[{referencia:'F3',tituloMaterial:'Limites e Derivadas',pagina:12,materialId:8}];
const tabela=String.raw`Por fatoração, o limite é $2$. [F3]

Exemplo visual didático criado pela IA, baseado no conceito em [F3].

| Etapa | Expressão | Explicação |
| --- | --- | --- |
| Fatoração | $\dfrac{x^2-1}{x-1}$ | Diferença de quadrados. [F3] |
| Resultado | $2$ | Substituição. [F3] |
[F3]`;

describe('Fontes legíveis do Monitor',()=>{
 it('limpa os códigos e a linha extra sem perder a tabela nem as frações',()=>{
  const {container}=render(<RespostaMonitor conteudo={tabela} fontes={fontes}/>);
  expect(container).not.toHaveTextContent('[F3]');
  expect(screen.getAllByRole('row')).toHaveLength(3);
  expect(container.querySelector('math mfrac')).not.toBeNull();
  expect(screen.getByText('Exemplo visual didático criado pela IA com base nos materiais consultados.')).toBeVisible();
  const detalhes=container.querySelector('details');
  expect(detalhes).not.toHaveAttribute('open');
  fireEvent.click(screen.getByText('De onde veio esta explicação?'));
  expect(detalhes).toHaveAttribute('open');
  expect(screen.getByText('Limites e Derivadas')).toBeVisible();
  expect(screen.getByText('Página 12')).toBeVisible();
  expect(screen.getByRole('link',{name:'Abrir material: Limites e Derivadas'})).toHaveAttribute('href','/api/v1/materiais/8/arquivo#page=12');
  expect(tabela).toContain('[F3]');
 });
 it('mostra fontes distintas por nome sem depender da numeração dos códigos',()=>{
  render(<RespostaMonitor conteudo={'Definição. [F7]\n\nExemplo. [F2]'} fontes={[
   {referencia:'F7',titulo_material:'Livro de Cálculo',pagina:30,material_id:10},
   {referencia:'F2',arquivo:'Aula 2.pdf',pagina:12,paginas_mescladas:[12,13],material_id:11}
  ]}/>);
  fireEvent.click(screen.getByText('De onde veio esta explicação?'));
  expect(screen.getByText('2 materiais consultados')).toBeVisible();
  expect(screen.getByText('Livro de Cálculo')).toBeVisible();
  expect(screen.getByText('Páginas 12, 13')).toBeVisible();
  expect(screen.getAllByRole('link')).toHaveLength(2);
 });
 it('preserva códigos literais em código e fórmulas',()=>{
  const {container}=render(<RespostaMonitor conteudo={'Use o vetor:\n\n```c\nvalor = F[3]; // [F3]\n```\n\n$[F3]$\n\nExplicação. [F3]'} fontes={fontes}/>);
  expect(container.querySelector('code')).toHaveTextContent('// [F3]');
  expect(container.querySelector('math')).not.toBeNull();
  expect(screen.getByText('Explicação.')).toBeVisible();
 });
 it('não inventa páginas ou links quando faltam metadados no histórico',()=>{
  render(<RespostaMonitor conteudo={'Explicação. [F3]'} fontes={[{arquivo:'Aula antiga.pdf'}]}/>);
  fireEvent.click(screen.getByText('De onde veio esta explicação?'));
  expect(screen.getByText('Aula antiga.pdf')).toBeVisible();
  expect(screen.queryByText(/^Página/)).not.toBeInTheDocument();
  expect(screen.queryByRole('link')).not.toBeInTheDocument();
  expect(screen.getByText('Documento sem link disponível nesta conversa.')).toBeVisible();
 });
});
