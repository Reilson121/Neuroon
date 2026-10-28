import copy
import random
import statistics
import unittest
from fractions import Fraction as F

from app.practice.math_engine import FAMILIAS, calcular, construir, quantil, verificar


class PracticeMathTests(unittest.TestCase):
    def test_medidas_e_convencao_de_quartis_conhecidas(self):
        valores=[2,4,6,8,10]
        for familia,esperado in [("media",6),("mediana",6),("amplitude",8),("variancia_populacional",8),("variancia_amostral",10)]:
            self.assertEqual(calcular({"familia":familia,"dados":{"valores":valores}}),esperado)
        dados=[2,3,5,7,9,11,13,15]
        self.assertEqual(quantil(dados,F(1,4)),F(9,2))
        self.assertEqual(quantil(dados,F(3,4)),F(23,2))
        self.assertEqual(calcular({"familia":"iqr","dados":{"valores":dados}}),7)

    def test_contagem_e_probabilidade(self):
        self.assertEqual(calcular({"familia":"arranjo","dados":{"n":15,"k":3}}),2730)
        self.assertEqual(calcular({"familia":"combinacao","dados":{"n":15,"k":3}}),455)
        self.assertEqual(calcular({"familia":"condicional","dados":{"ambos":6,"condicao":20}}),F(3,10))
        self.assertEqual(calcular({"familia":"sem_reposicao","dados":{"azuis":4,"vermelhas":6,"total":10}}),F(4,15))

    def test_todas_as_familias_com_dados_variados(self):
        for familias in FAMILIAS.values():
            for familia in familias:
                for seed in range(40):
                    with self.subTest(familia=familia,seed=seed):
                        q=construir(familia,random.Random(seed))
                        self.assertTrue(verificar(q))
                        self.assertTrue(q['formula'])
                        self.assertTrue(q['calculos'])
                        self.assertTrue(q['dica'])
                        if familia=='correlacao':
                            d=q['spec']['dados']
                            self.assertAlmostEqual(calcular(q['spec']),statistics.correlation(d['valores'],d['y']),places=9)

    def test_rejeita_gabarito_e_alternativas_adulterados(self):
        q=construir('media',random.Random(2));alterado=copy.deepcopy(q)
        alterado['gabarito']=next(k for k in alterado['alternativas'] if k!=q['gabarito'])
        with self.assertRaises(ValueError):verificar(alterado)
        alterado=copy.deepcopy(q);alterado['alternativas']['A']=alterado['alternativas']['B']
        with self.assertRaises(ValueError):verificar(alterado)

    def test_quartis_informam_metodo_antes_da_resposta_e_detalham_interpolacao(self):
        q=construir('iqr',random.Random(7))
        self.assertIn('h=(n−1)q',q['enunciado'])
        self.assertIn('índice iniciado em zero',q['enunciado'])
        self.assertIn('interpolação linear',q['enunciado'])
        self.assertTrue(any('Interpolação:' in passo for passo in q['calculos']))


if __name__=='__main__':unittest.main()
