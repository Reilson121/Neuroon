import React from 'react';
import {render,screen} from '@testing-library/react';
import {describe,expect,it} from 'vitest';
import Texto from './Texto.jsx';

describe('Notação matemática nas explicações',()=>{
 it('mostra o limite com fração vertical e preserva a citação',()=>{
  const {container}=render(<Texto>{String.raw`Portanto, $\lim_{x \to 1} \dfrac{x^2 - 1}{x - 1} = 2$. [F2]`}</Texto>);
  expect(container.querySelector('math mfrac')).not.toBeNull();
  expect(container.querySelector('math msup')).not.toBeNull();
  expect(container.querySelector('.katex-error')).toBeNull();
  expect(screen.getByText(/\[F2\]/)).toBeVisible();
 });
 it('renderiza frações dentro da tabela de passos',()=>{
  const {container}=render(<Texto>{String.raw`| Etapa | Expressão |
| --- | --- |
| Substituição | $\dfrac{1^2 - 1}{1 - 1} = \dfrac{0}{0}$ |`}</Texto>);
  expect(screen.getByRole('table')).toBeVisible();
  expect(container.querySelectorAll('td math mfrac')).toHaveLength(2);
 });
 it('aceita fórmulas destacadas e alternativas inline',()=>{
  const {container}=render(<Texto inline>{String.raw`$\sqrt{x} + \dfrac{1}{2}$`}</Texto>);
  expect(container.querySelector('p')).toBeNull();
  expect(container.querySelector('math msqrt')).not.toBeNull();
 });
 it('não interpreta divisões comuns, caminhos e código como matemática',()=>{
  const {container}=render(<Texto>{'Indeterminação 0/0. Consulte aula/limites.\n\n`(x - 1)/(x - 1)`'}</Texto>);
  expect(container.querySelector('.katex')).toBeNull();
  expect(screen.getByText('(x - 1)/(x - 1)').tagName).toBe('CODE');
 });
 it('mantém a resposta legível com expressão incompleta durante o envio',()=>{
  const {container,rerender}=render(<Texto>{String.raw`Resultado: $\dfrac{x`}</Texto>);
  expect(container).toHaveTextContent('Resultado:');
  rerender(<Texto>{String.raw`Resultado: $\dfrac{x}{2}$`}</Texto>);
  expect(container.querySelector('math mfrac')).not.toBeNull();
 });
 it('não permite comandos LaTeX criarem links arbitrários',()=>{
  const {container}=render(<Texto>{String.raw`$\href{https://example.com}{x}$`}</Texto>);
  expect(container.querySelector('a')).toBeNull();
 });
});
