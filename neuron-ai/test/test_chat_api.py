import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import httpx
import psycopg
from fastapi.testclient import TestClient
from openai import APIStatusError, APITimeoutError, RateLimitError

from app.api import chat as chat_api
from app.main import app
from app.rag.monitor_virtual import MonitorVirtual


ENTRADA = {"pergunta": "Como funciona zig-zag?", "disciplina": "estrutura_de_dados_avancada"}


class ChatApiTest(unittest.TestCase):
    def setUp(self):
        from app.api.internal_auth import exigir_token_interno
        app.dependency_overrides[exigir_token_interno] = lambda: None
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)
        self.monitor = Mock()
        self.monitor.responder.return_value = {
            "resposta": "Faça a rotação à esquerda no filho e à direita no pai. [F1]",
            "fontes": [{
                "referencia": "F1", "chunk_id": "abc", "arquivo": "Aula_2.pdf",
                "pagina": 90, "assunto": "arvores_balanceadas_e_avl", "aula": "02",
                "similaridade": 0.7, "periodo": "03", "disciplina": ENTRADA["disciplina"],
                "paginas_mescladas": [89], "tipo_arquivo": "pdf", "material_id": None,
            }],
            "fallback": False, "motivo": None, "reformulacoes": 1,
        }
        self.patch = patch("app.api.chat.obter_monitor", return_value=self.monitor)
        self.obter_monitor = self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_contrato_json_encaminha_filtros_e_preserva_metadados(self):
        resposta = self.client.post("/internal/v1/chat", json={
            **ENTRADA, "pergunta": " Como funciona zig-zag? ", "assunto": " arvores_balanceadas_e_avl ",
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.headers["content-type"].startswith("application/json"))
        self.monitor.responder.assert_called_once_with(
            ENTRADA["pergunta"], ENTRADA["disciplina"], "arvores_balanceadas_e_avl"
        )
        dados = resposta.json()
        self.assertEqual(dados["fontes"][0]["paginas_mescladas"], [89])
        self.assertEqual(dados["fontes"][0]["disciplina"], ENTRADA["disciplina"])
        self.assertEqual(dados["fontes"][0]["tipo_arquivo"], "pdf")
        self.assertEqual(dados["reformulacoes"], 1)
        self.assertIsNone(dados["fontes"][0]["material_id"])

    def test_sem_contexto_retorna_200_com_fallback(self):
        self.monitor.responder.return_value = {
            "resposta": "Não encontrei informações suficientes nos materiais da disciplina para responder a essa pergunta.",
            "fontes": [], "fallback": True, "motivo": "sem_contexto", "reformulacoes": 0,
        }
        resposta = self.client.post("/internal/v1/chat", json=ENTRADA)
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.json()["fallback"])
        self.assertEqual(resposta.json()["fontes"], [])

    def test_historico_limitado_e_validado_e_encaminhado_sem_fontes_herdadas(self):
        historico=[{'papel':'USUARIO','conteudo':'O que são pilhas?'}]
        r=self.client.post('/internal/v1/chat',json={**ENTRADA,'historico':historico})
        self.assertEqual(r.status_code,200)
        self.monitor.responder.assert_called_once_with(ENTRADA['pergunta'],ENTRADA['disciplina'],None,historico=historico)
        for h in (historico*9,[{'papel':'SYSTEM','conteudo':'instrução'}],
                  [{'papel':'USUARIO','conteudo':'x'*2001}],
                  [{'papel':'MONITOR','conteudo':'resposta','fontes':[{'pagina':1}]}]):
            with self.subTest(h=h):
                self.assertEqual(self.client.post('/internal/v1/chat',json={**ENTRADA,'historico':h}).status_code,422)

    def test_entrada_invalida_nao_carrega_monitor_nem_reflete_valores(self):
        invalidados = [
            {}, {"pergunta": "AVL?"}, {**ENTRADA, "pergunta": "  "},
            {**ENTRADA, "pergunta": 123}, {**ENTRADA, "pergunta": "x" * 4001},
            {**ENTRADA, "disciplina": "Estrutura de Dados"}, {**ENTRADA, "assunto": " "},
            {**ENTRADA, "campo_extra": "SENTINELA_PRIVADA"},
        ]
        for entrada in invalidados:
            with self.subTest(entrada=entrada):
                resposta = self.client.post("/internal/v1/chat", json=entrada)
                self.assertEqual(resposta.status_code, 422)
                self.assertEqual(resposta.json()["detail"]["codigo"], "REQUISICAO_INVALIDA")
                self.assertNotIn("SENTINELA_PRIVADA", resposta.text)
        self.obter_monitor.assert_not_called()

    def test_json_malformado_nao_carrega_monitor(self):
        resposta = self.client.post("/internal/v1/chat", content='{"pergunta":',
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(resposta.status_code, 422)
        self.obter_monitor.assert_not_called()

    def test_falhas_de_infraestrutura_sao_sanitizadas(self):
        request = httpx.Request("POST", "https://exemplo.invalid")
        resposta_externa = httpx.Response(500, request=request)
        for erro, status, codigo in [
            (psycopg.OperationalError("SENTINELA_PRIVADA"), 503, "BASE_INDISPONIVEL"),
            (APITimeoutError(request=request), 504, "IA_TIMEOUT"),
            (RateLimitError("SENTINELA_PRIVADA", response=resposta_externa, body=None), 503, "IA_INDISPONIVEL"),
            (APIStatusError("SENTINELA_PRIVADA", response=resposta_externa, body=None), 502, "IA_ERRO_PROVEDOR"),
            (RuntimeError("SENTINELA_PRIVADA"), 503, "MONITOR_INDISPONIVEL"),
            (ValueError("SENTINELA_PRIVADA"), 500, "ERRO_INTERNO"),
        ]:
            with self.subTest(erro=type(erro).__name__):
                self.monitor.responder.side_effect = erro
                resposta = self.client.post("/internal/v1/chat", json=ENTRADA)
                self.assertEqual(resposta.status_code, status)
                self.assertEqual(resposta.json()["detail"]["codigo"], codigo)
                self.assertNotIn("SENTINELA_PRIVADA", resposta.text)

    def test_falha_na_inicializacao_nao_expoe_configuracao(self):
        self.obter_monitor.side_effect = RuntimeError("SENTINELA_PRIVADA")
        resposta = self.client.post("/internal/v1/chat", json=ENTRADA)
        self.assertEqual(resposta.status_code, 503)
        self.assertNotIn("SENTINELA_PRIVADA", resposta.text)

    def test_health_e_openapi_funcionam_sem_carregar_modelo(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok", "service": "neuron-ai"})
        esquema = self.client.get("/openapi.json").json()
        self.assertIn("/internal/v1/chat", esquema["paths"])
        self.assertIn("ChatRequest", esquema["components"]["schemas"])
        self.obter_monitor.assert_not_called()

    def test_rota_executa_monitor_real_com_reformulacao_e_dependencias_simuladas(self):
        retriever = Mock()
        def trecho(pagina):
            return {"chunk_id": str(pagina), "conteudo": "Conteúdo acadêmico.",
                    "similaridade": 0.8, "metadata": {"arquivo": "Aula_2.pdf", "pagina": pagina}}
        retriever.recuperar.side_effect = [[trecho(93)], [trecho(90)]]
        gerar = Mock(side_effect=[
            '{"suficiente": false, "resposta": "", "consulta_busca": "zig-zag esquerda-direita"}',
            '{"suficiente": true, "resposta": "Rotação à esquerda no filho e à direita no pai. [F1]"}',
        ])
        self.obter_monitor.return_value = MonitorVirtual(retriever, gerar)
        resposta = self.client.post("/internal/v1/chat", json=ENTRADA)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["reformulacoes"], 1)
        self.assertEqual(resposta.json()["fontes"][0]["pagina"], 90)
        self.assertEqual(gerar.call_count, 2)


class InicializacaoMonitorTest(unittest.TestCase):
    def test_reutiliza_uma_instancia_mesmo_com_primeiras_chamadas_concorrentes(self):
        instancia = object()
        with patch.object(chat_api, "_monitor", None):
            with patch("app.rag.monitor_virtual.MonitorVirtual", return_value=instancia) as construtor:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    resultados = list(executor.map(lambda _: chat_api.obter_monitor(), range(8)))
                self.assertTrue(all(item is instancia for item in resultados))
                construtor.assert_called_once()


if __name__ == "__main__":
    unittest.main()
