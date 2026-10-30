import unittest
from app.rag.calculo_search import ordenar_evidencias


def fonte(arquivo,pagina):return dict(arquivo=arquivo,pagina=pagina)


class CalculoSearchTests(unittest.TestCase):
    def test_cadeia_nao_recebe_exercicio_de_hiperbolicas(self):
        linhas=[fonte('03 regras de derivação.pdf',80),fonte('Tabela de Derivadas do Prof. Douglas Maioli.pdf',1),fonte('03 regras de derivação.pdf',23)]
        r=ordenar_evidencias(linhas,'Explique a regra da cadeia e indique a tabela de apoio.',5)
        self.assertEqual(r,linhas[1:])

    def test_produto_quociente_e_potencia_tem_suas_secoes(self):
        linhas=[fonte('03 regras de derivação.pdf',23),fonte('03 regras de derivação.pdf',11),fonte('03 regras de derivação.pdf',2)]
        for nome,indice in [('produto',1),('quociente',1),('potência',2)]:
            self.assertEqual(ordenar_evidencias(linhas,'Qual é a regra do '+nome+'?' if indice==1 else 'Regra da potência',5),[linhas[indice]])

    def test_demais_perguntas_preservam_busca_e_limite(self):
        linhas=[fonte('prova_calculo_transcrita.pdf',2),fonte('02 Limites e Derivadas.pdf',35)]
        self.assertEqual(ordenar_evidencias(linhas,'Questão 8 da prova?',1),linhas[:1])
