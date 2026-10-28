import unittest
from unittest.mock import Mock
import json

from app.rag.hybrid_search import ordenar_hibrido, termos
from app.rag.retriever import Retriever
from app.rag.monitor_virtual import MonitorVirtual


class HybridSearchTest(unittest.TestCase):
    def test_reduz_modelos_repetidos_sem_descartar_definicao_distinta(self):
        modelo = "Matriz CSD Certezas sabemos entendemos Suposições supomos Dúvidas temos dúvidas campos"
        linhas = [{"chunk_id": str(i), "conteudo": modelo, "similaridade": .9 - i * .01} for i in range(10)]
        linhas.append({"chunk_id": "definicao", "conteudo": "Suposições são hipóteses plausíveis e testáveis.",
                       "similaridade": .5})
        resultado = ordenar_hibrido(linhas, "Certezas suposições dúvidas matriz CSD", 5)
        self.assertIn("definicao", [r["chunk_id"] for r in resultado])
        self.assertEqual(sum(r["conteudo"] == modelo for r in resultado), 1)

    def test_evidencia_literal_nao_e_descartada_por_cosseno_baixo(self):
        recuperador = Mock()
        recuperador.recuperar.return_value = [{
            "chunk_id": "fechamento", "conteudo": "FECHAMENTO: contornos completados pelo cérebro.",
            "metadata": {"arquivo": "Aula_05.pdf", "pagina": 38},
            "similaridade": .18, "cobertura_lexical": .7,
        }]
        gerar = Mock(return_value=json.dumps({"suficiente": True, "resposta": "Contornos completados pelo cérebro. [F1]"}))
        resultado = MonitorVirtual(recuperador, gerar=gerar).responder("Fechamento na Gestalt?", "design_de_artefatos_digitais")
        self.assertFalse(resultado["fallback"])
        self.assertEqual(resultado["fontes"][0]["similaridade"], .18)
        gerar.assert_called_once()

    def test_json_com_cerca_inteira_e_aceito_mas_prosa_externa_e_recusada(self):
        bruto = '```json\n{"suficiente": true, "resposta": "Três cores equidistantes. [F1]"}\n```'
        fontes = {"F1": {"referencia": "F1", "pagina": 31}}
        self.assertFalse(MonitorVirtual._interpretar_resposta(bruto, fontes)["fallback"])
        self.assertEqual(MonitorVirtual._interpretar_resposta("Resposta: " + bruto, fontes)["motivo"],
                         "formato_invalido")

    def test_termo_especifico_recupera_definicao_ausente_do_top_vetorial(self):
        linhas = [{"chunk_id": str(i), "conteudo": "Design visual e composição", "similaridade": 0.6 - i * .001}
                  for i in range(30)]
        linhas.append({"chunk_id": "fechamento", "conteudo": "FECHAMENTO: contornos ausentes solucionados pelo cérebro.",
                       "similaridade": 0.3})
        resultado = ordenar_hibrido(linhas, "O que é fechamento na Gestalt?", 5)
        self.assertIn("fechamento", [r["chunk_id"] for r in resultado])
        self.assertEqual(next(r for r in resultado if r["chunk_id"] == "fechamento")["similaridade"], 0.3)

    def test_sem_termos_literais_preserva_ordem_por_similaridade(self):
        linhas = [{"chunk_id": "a", "conteudo": "tipografia", "similaridade": .2},
                  {"chunk_id": "b", "conteudo": "interfaces", "similaridade": .8}]
        self.assertEqual([r["chunk_id"] for r in ordenar_hibrido(linhas, "capital França", 5)], ["b", "a"])
        self.assertEqual(termos("Quais são os princípios da GESTALT?"), ["principios", "gestalt"])

    def test_perfil_design_encaminha_pergunta_e_filtros_sem_alterar_fontes(self):
        embedder, store = Mock(), Mock()
        embedder.gerar_embedding.return_value = [1, 0]
        store.buscar_hibridos.return_value = [{
            "chunk_id": "a", "conteudo": "Matriz CSD", "similaridade": .7,
            "disciplina": "design_de_artefatos_digitais", "assunto": "matriz_csd",
            "arquivo": "MATRIZ_CSD.pdf", "pagina": 26, "metadata": {},
        }]
        resultado = Retriever(embedder, store).recuperar(" Linhas da CSD? ", "design_de_artefatos_digitais", "matriz_csd")
        store.buscar_hibridos.assert_called_once_with([1, 0], "Linhas da CSD?", "design_de_artefatos_digitais",
                                                      assunto="matriz_csd", k=5)
        store.buscar_similares.assert_not_called()
        self.assertEqual(resultado[0]["metadata"]["pagina"], 26)


if __name__ == "__main__":
    unittest.main()
