import json
import unittest
from unittest.mock import Mock, call

from app.rag.monitor_virtual import MonitorVirtual


def chunk(identificador, pagina):
    return {
        "chunk_id": identificador, "conteudo": "Material acadêmico da página.",
        "similaridade": 0.8,
        "metadata": {"arquivo": "Aula_2.pdf", "pagina": pagina,
                     "assunto": "arvores_balanceadas_e_avl",
                     "disciplina": "estrutura_de_dados_avancada"},
    }


def insuficiente(consulta):
    return json.dumps({"suficiente": False, "resposta": "", "consulta_busca": consulta})


class ReformulacaoTest(unittest.TestCase):
    def setUp(self):
        self.retriever = Mock()
        self.retriever.recuperar.return_value = [chunk("inicial", 93)]
        self.gerar = Mock()
        self.monitor = MonitorVirtual(self.retriever, self.gerar)

    def test_reformula_busca_preserva_pergunta_e_filtros_e_cita_nova_pagina(self):
        pergunta = "Como funciona zig-zag em AVL?"
        self.retriever.recuperar.side_effect = [[chunk("inicial", 93)], [chunk("correto", 90)]]
        self.gerar.side_effect = [insuficiente("zig-zag esquerda-direita"), json.dumps({
            "suficiente": True, "resposta": "Rotação à esquerda no filho e à direita no pai. [F1]"
        })]
        resultado = self.monitor.responder(pergunta, "estrutura_de_dados_avancada", "avl")
        self.assertFalse(resultado["fallback"])
        self.assertEqual(resultado["reformulacoes"], 1)
        self.assertEqual(resultado["fontes"][0]["pagina"], 90)
        self.assertEqual(resultado["fontes"][0]["chunk_id"], "correto")
        self.assertEqual(self.retriever.recuperar.call_args_list, [
            call(pergunta, "estrutura_de_dados_avancada", "avl", k=5),
            call("zig-zag esquerda-direita", "estrutura_de_dados_avancada", "avl", k=5),
        ])
        for chamada in self.gerar.call_args_list:
            self.assertIn(pergunta, chamada.args[0].to_messages()[-1].content)
        self.assertNotIn("consulta_busca", resultado)

    def test_limita_a_duas_reformulacoes(self):
        self.gerar.side_effect = [insuficiente("zig-zag"), insuficiente("rotações compostas"),
                                 insuficiente("outra consulta que não deve executar")]
        resultado = self.monitor.responder("Como funciona AVL?", "ed")
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["fontes"], [])
        self.assertEqual(resultado["reformulacoes"], 2)
        self.assertEqual(self.retriever.recuperar.call_count, 3)
        self.assertEqual(self.gerar.call_count, 3)

    def test_nao_repete_consulta_equivalente(self):
        self.gerar.return_value = insuficiente("  ZIG ZAG!!! ")
        resultado = self.monitor.responder("Zig-zag?", "ed")
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["reformulacoes"], 0)
        self.retriever.recuperar.assert_called_once()

    def test_consulta_ausente_invalida_ou_longa_nao_gera_nova_busca(self):
        for consulta in [None, " ", 123, ["zig-zag"], "x" * 241]:
            with self.subTest(consulta=consulta):
                self.retriever.reset_mock()
                self.gerar.return_value = insuficiente(consulta)
                resultado = self.monitor.responder("AVL?", "ed")
                self.assertTrue(resultado["fallback"])
                self.retriever.recuperar.assert_called_once()

    def test_busca_reformulada_sem_contexto_nao_chama_modelo_novamente(self):
        self.retriever.recuperar.side_effect = [[chunk("inicial", 93)], []]
        self.gerar.return_value = insuficiente("zig-zag")
        resultado = self.monitor.responder("Como funciona AVL?", "ed")
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["motivo"], "sem_contexto")
        self.assertEqual(resultado["reformulacoes"], 1)
        self.gerar.assert_called_once()


if __name__ == "__main__":
    unittest.main()
