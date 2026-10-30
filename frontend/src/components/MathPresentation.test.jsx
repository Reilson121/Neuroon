import React from 'react';
import {render,cleanup,screen,fireEvent} from '@testing-library/react';
import {expect,it} from 'vitest';
import Texto from './Texto.jsx';
import ApoioEstatistica from './ApoioEstatistica.jsx';
import fixtures from '../math-presentation-fixtures.json';

it('renderiza as saídas reais dos três motores sem erros de LaTeX',()=>{
 for(const item of fixtures){
  const {container}=render(<>{item.campos.map((s,i)=><Texto key={i}>{s}</Texto>)}</>);
  expect(container.querySelector('.katex-error'),`${item.motor}/${item.topico}/${item.tipo}`).toBeNull();
  expect(container.querySelector('math'),`${item.motor}/${item.topico}/${item.tipo}`).not.toBeNull();
  cleanup();
 }
});
it('oferece os slides de Estatística na página do conteúdo escolhido',()=>{
 render(<ApoioEstatistica materiais={[{id:90,tipo:'SLIDE_AULA',arquivoDisponivel:true}]} assuntos={[{id:6,ordem:6,nome:'Médias'},{id:9,ordem:9,nome:'Correlação'}]} assuntoId={9}/>);
 fireEvent.click(screen.getByText('Consultar fórmulas e tabelas de Estatística'));
 expect(screen.getByRole('link',{name:/Correlação.*44/})).toHaveAttribute('href','/api/v1/materiais/90/arquivo#page=44');
 fireEvent.change(screen.getByLabelText('Conteúdo da consulta'),{target:{value:6}});
 expect(screen.getByRole('link',{name:/Médias.*30/})).toHaveAttribute('href','/api/v1/materiais/90/arquivo#page=30');
});
it('não inventa link de tabela quando o material não está disponível',()=>{
 const {container}=render(<ApoioEstatistica assuntos={[{id:6,ordem:6,nome:'Médias'}]}/>);
 expect(container).toBeEmptyDOMElement();
});
it('mantém as duas colunas e todas as observações na tabela de correlação',()=>{
 const caso=fixtures.find(q=>q.motor==='estatistica'&&q.topico==='correlacao');
 render(<Texto>{caso.campos[0]}</Texto>);
 const table=screen.getByRole('table');
 expect(table.querySelectorAll('tbody tr')).toHaveLength(5);
 table.querySelectorAll('tbody tr').forEach(row=>expect(row.querySelectorAll('td')).toHaveLength(2));
});
