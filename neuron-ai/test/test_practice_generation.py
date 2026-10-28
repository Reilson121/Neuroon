import json
import unittest
from unittest.mock import patch
from app.practice.generation import contextos_ia

class PracticeGenerationTests(unittest.TestCase):
    @patch('app.rag.monitor_virtual.MonitorVirtual._gerar_openrouter')
    def test_repete_formato_invalido_uma_vez_sem_liberar_saida_invalida(self,gerar):
        frase='Uma equipe analisa registros para planejar melhorias.'
        gerar.side_effect=[json.dumps({'contextos':[frase]*10}),json.dumps({'contextos':[frase]})]
        self.assertEqual(contextos_ia([{'conceito':'Amplitude'}]),[frase])
        self.assertEqual(gerar.call_count,2)
        self.assertIn('resposta anterior foi recusada',gerar.call_args.args[0].to_messages()[-1].content)

    @patch('app.rag.monitor_virtual.MonitorVirtual._gerar_openrouter')
    def test_informa_quantidade_exata_inclusive_uma_questao(self,gerar):
        frase='Uma equipe analisa registros para planejar melhorias.'
        for n in [1,5,10]:
            gerar.return_value=json.dumps({'contextos':[frase]*n})
            self.assertEqual(contextos_ia([{'conceito':'Amplitude'}]*n),[frase]*n)
            mensagens=' '.join(m.content for m in gerar.call_args.args[0].to_messages())
            self.assertIn(f'exatamente {n} frases',mensagens)
            self.assertIn(f'Quantidade obrigatória de contextos: {n}',mensagens)

    @patch('app.rag.monitor_virtual.MonitorVirtual._gerar_openrouter')
    def test_rejeita_variacoes_extras_e_condicoes_inventadas(self,gerar):
        for dados in [
            {'contextos':['Uma equipe analisa registros.']*10},
            {'contextos':['Considere 50 registros para a análise.']},
            {'contextos':['Considere retiradas com reposição neste caso.']},
            {'contextos':['Uma equipe analisa registros.'],'gabarito':'A'},
        ]:
            gerar.return_value=json.dumps(dados)
            with self.assertRaises(ValueError):contextos_ia([{'conceito':'Amplitude'}])
