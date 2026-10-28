import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

from app.rag.monitor_virtual import GeracaoIncompleta, MENSAGEM_FALLBACK, MonitorVirtual


def chunk(identificador="a", similaridade=0.8, pagina=84):
    return {
        "chunk_id": identificador, "conteudo": "AVL é uma árvore balanceada.",
        "similaridade": similaridade,
        "metadata": {"arquivo": "Aula_2.pdf", "pagina": pagina,
                     "assunto": "arvores_balanceadas_e_avl", "aula": "02",
                     "periodo": "03", "disciplina": "estrutura_de_dados_avancada",
                     "tipo_arquivo": "pdf", "tipo_extracao": "textual",
                     "paginas_mescladas": [83]},
    }


class MonitorVirtualTest(unittest.TestCase):
    def setUp(self):
        self.retriever = Mock()
        self.retriever.recuperar.return_value = [chunk()]
        self.gerar = Mock(return_value=json.dumps({
            "suficiente": True, "resposta": "É uma árvore balanceada. [F1]"
        }))
        self.monitor = MonitorVirtual(self.retriever, self.gerar)

    def test_resposta_cita_somente_fontes_usadas_e_preserva_origem(self):
        self.retriever.recuperar.return_value = [chunk(), chunk("b", pagina=85)]
        resultado = self.monitor.responder("AVL?", "estrutura_de_dados_avancada")
        self.assertFalse(resultado["fallback"])
        self.assertEqual(len(resultado["fontes"]), 1)
        self.assertEqual(resultado["fontes"][0]["pagina"], 84)
        self.assertEqual(resultado["fontes"][0]["paginas_mescladas"], [83])
        self.assertEqual(resultado["fontes"][0]["chunk_id"], "a")
        prompt = self.gerar.call_args.args[0].to_messages()
        self.assertIn("AVL?", prompt[1].content)
        self.assertIn("Aula_2.pdf", prompt[1].content)

    def test_sem_contexto_nao_chama_modelo(self):
        for chunks in [[], [chunk(similaridade=0.1)], [chunk(pagina=None)]]:
            with self.subTest(chunks=chunks):
                self.retriever.recuperar.return_value = chunks
                resultado = self.monitor.responder("AVL?", "ed")
                self.assertEqual(resultado["resposta"], MENSAGEM_FALLBACK)
                self.assertEqual(resultado["fontes"], [])
        self.gerar.assert_not_called()

    def test_modelo_declara_insuficiencia(self):
        self.gerar.return_value = '{"suficiente": false, "resposta": ""}'
        resultado = self.monitor.responder("Pergunta fora do tema", "ed")
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["fontes"], [])
        self.assertEqual(resultado["motivo"], "contexto_insuficiente")

    def test_rejeita_referencia_inventada_ou_ausente(self):
        for texto in ["AVL. [F99]", "AVL."]:
            with self.subTest(texto=texto):
                self.gerar.return_value = json.dumps({"suficiente": True, "resposta": texto})
                resultado = self.monitor.responder("AVL?", "ed")
                self.assertTrue(resultado["fallback"])
                self.assertEqual(resultado["fontes"], [])
                self.assertEqual(resultado["motivo"], "fontes_invalidas")

    def test_remove_conclusao_sem_fonte_preservando_explicacao_citada(self):
        self.gerar.return_value = json.dumps({
            "suficiente": True,
            "resposta": "AVL é balanceada. [F1]\n\nConclusão não apoiada nos materiais.",
        })
        resultado = self.monitor.responder("AVL?", "ed")
        self.assertFalse(resultado["fallback"])
        self.assertEqual(resultado["resposta"], "AVL é balanceada. [F1]")
        self.assertEqual(resultado["blocos_sem_fonte_removidos"], 1)

    def test_resposta_vazia_malformada_ou_truncada(self):
        for bruto in ["", '{"suficiente":', '[]', 'null',
                      '{"suficiente": "true", "resposta": "AVL [F1]"}',
                      '{"suficiente": true, "resposta": 123}']:
            with self.subTest(bruto=bruto):
                self.gerar.return_value = bruto
                resultado = self.monitor.responder("AVL?", "ed")
                self.assertTrue(resultado["fallback"])
                self.assertEqual(resultado["fontes"], [])

    def test_formula_removida_nao_retorna_somente_legenda_como_resposta(self):
        self.gerar.return_value = json.dumps({"suficiente": True,
            "resposta": "Erro padrão:\n\n\\[sigma/sqrt(n)\\]\n\nem que sigma é o desvio populacional e n o tamanho da amostra. [F1]"})
        resultado = self.monitor.responder("Qual é a fórmula do erro padrão?", "estatistica")
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["motivo"], "formato_invalido")
        self.assertEqual(resultado["fontes"], [])

    def test_falha_de_infraestrutura_nao_vira_falta_de_contexto(self):
        self.gerar.side_effect = RuntimeError("Serviço indisponível")
        with self.assertRaises(RuntimeError):
            self.monitor.responder("AVL?", "ed")

    def test_geracao_incompleta_tem_motivo_distinto_de_falta_de_contexto(self):
        self.gerar.side_effect = GeracaoIncompleta()
        resultado = self.monitor.responder("AVL?", "ed")
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["motivo"], "geracao_incompleta")
        self.assertEqual(resultado["fontes"], [])
        self.assertNotEqual(resultado["resposta"], MENSAGEM_FALLBACK)

    def test_adapter_reserva_orcamento_para_resposta_e_rejeita_truncamento(self):
        configuracao = SimpleNamespace(OPENROUTER_API_KEY="chave-ficticia-teste",
                                      OPENROUTER_MODEL="modelo-ficticio-teste")
        cliente = MagicMock()
        cliente.__enter__.return_value = cliente
        resposta = SimpleNamespace(choices=[SimpleNamespace(
            finish_reason="stop", message=SimpleNamespace(content='{"suficiente": false}')
        )])
        cliente.chat.completions.create.return_value = resposta
        prompt = Mock()
        prompt.to_messages.return_value = [SimpleNamespace(type="system", content="Teste")]
        with patch.dict("sys.modules", {"app.config.settings": configuracao}):
            with patch("openai.OpenAI", return_value=cliente):
                self.assertEqual(MonitorVirtual._gerar_openrouter(prompt), '{"suficiente": false}')
                chamada = cliente.chat.completions.create.call_args.kwargs
                self.assertEqual(chamada["extra_body"], {"reasoning": {"enabled": False}})
                resposta.choices[0].finish_reason = "length"
                with self.assertRaises(GeracaoIncompleta):
                    MonitorVirtual._gerar_openrouter(prompt)


if __name__ == "__main__":
    unittest.main()
