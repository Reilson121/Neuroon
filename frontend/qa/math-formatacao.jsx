import React from 'react';
import {createRoot} from 'react-dom/client';
import Texto from '../src/components/Texto.jsx';
import dados from '../src/math-presentation-fixtures.json';
const casos=[dados.find(q=>q.topico==='racionalizacao'),dados.find(q=>q.topico==='correlacao'),dados.find(q=>q.topico==='integral_definida'&&q.tipo==='RADICAL')];
createRoot(document.getElementById('root')).render(<main style={{maxWidth:1000,margin:'32px auto',fontFamily:'Arial',color:'#172d4d',background:'#fff'}}><h1>Notação matemática nas práticas</h1>{casos.map(q=><section key={q.topico} style={{padding:24,border:'1px solid #d7dfec',borderRadius:16,marginBottom:20,lineHeight:1.9}}><h2>{q.motor==='estatistica'?'Estatística':q.motor==='integral'?'Cálculo II':'Cálculo I'}</h2><Texto>{q.campos[0]}</Texto><Texto>{q.campos[1]}</Texto><Texto>{q.campos.at(-1)}</Texto></section>)}</main>);
