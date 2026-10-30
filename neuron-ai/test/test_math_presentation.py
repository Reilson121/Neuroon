import copy
import json
import random
import re
import unittest
from pathlib import Path
from app.practice.math_presentation import present,format_text,expression
from app.practice import calculo_engine as calc, integral_engine as integral, math_engine as stats

def samples():
 out=[]
 for engine,motor in [(calc,'calculo'),(integral,'integral')]:
  for topic,(_,_,_,types) in engine.TOPICOS.items():
   for kind in types:
    spec=dict(motor=motor,topico=topic,tipo_funcao=kind,parametros=[3,2,4,5])
    q=engine.construir(spec,random.Random(7));assert engine.verificar(q)
    out.append((motor,topic,kind,q))
 for family in [f for fs in stats.FAMILIAS.values() for f in fs]:
  out.append(('estatistica',family,'',stats.construir(family,random.Random(7))))
 return out

class MathPresentationTests(unittest.TestCase):
 def test_todos_os_motores_preservam_calculos_e_apresentam_alternativas(self):
  fixtures=[]
  for motor,topic,kind,q in samples():
   original=copy.deepcopy(q);view=present(q)
   self.assertEqual(q,original)
   self.assertEqual(view['gabarito'],q['gabarito']);self.assertEqual(view['fingerprint'],q['fingerprint'])
   for value in view['alternativas'].values():
    self.assertEqual(value.count('$')%2,0,(motor,topic,value))
    self.assertNotIn('sqrt(',value)
   fields=[view['enunciado'],view['formula'],*view['calculos'],*view['alternativas'].values()]
   self.assertTrue(any('$' in f for f in fields),(motor,topic))
   fixtures.append(dict(motor=motor,topico=topic,tipo=kind,campos=fields))
  target=Path(__file__).resolve().parents[2]/'frontend/src/math-presentation-fixtures.json'
  target.write_text(json.dumps(fixtures,ensure_ascii=False,indent=2),encoding='utf-8')

 def test_limite_do_print_tem_raiz_fracao_e_limite(self):
  q=calc.construir(dict(motor='calculo',topico='racionalizacao',tipo_funcao='RADICAL',parametros=[1,22,4,5]),random.Random(1))
  view=present(q)
  for command in [r'\lim',r'\sqrt',r'\dfrac']:self.assertIn(command,view['enunciado'])
  self.assertNotIn('sqrt(',view['enunciado'])
  self.assertTrue(all(v.startswith('$') and v.endswith('$') for v in view['alternativas'].values()))

 def test_notacao_do_slide_de_correlacao_e_variancia(self):
  q=stats.construir('correlacao',random.Random(1));formula=present(q)['formula']
  self.assertIn(r'\bar{x}',formula);self.assertIn('(n-1)S_xS_y',formula)
  for family,expected in [('variancia_populacional',r'\sigma^2'),('variancia_amostral','s^2')]:
   self.assertIn(expected,present(stats.construir(family,random.Random(1)))['formula'])

 def test_parser_preserva_markdown_codigos_links_e_nao_executa_texto(self):
  raw='Consulte https://example.com/a/b. `(x+1)/2` e $x^2$.'
  self.assertEqual(format_text(raw),raw)
  self.assertEqual(expression('-1/2'),r'$\dfrac{-1}{2}$')
  self.assertIn(r'f\left(1 , 2 , 3\right)',format_text('Calcule f(1,2,3).'))
  self.assertIn('__import__',format_text("__import__('os').system('segredo')"))

 def test_preserva_colunas_de_tabelas_e_formulas_ja_delimitadas(self):
  table='| X | Y |\n|---|---|\n| -2 | 3 |\n| 1/2 | 3/4 |'
  formatted=format_text(table)
  self.assertEqual([line.count('|') for line in table.splitlines()],[line.count('|') for line in formatted.splitlines()])
  self.assertNotIn(r'\mid',formatted)
  block=r'$$P(A\mid B)=\dfrac{P(A\cap B)}{P(B)}$$ [F1]'
  self.assertEqual(format_text(block),block)
  self.assertIn(r'\mid',format_text('P(A|B)=1/2'))

if __name__=='__main__':unittest.main()
