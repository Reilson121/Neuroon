import unittest
from unittest.mock import Mock

from app.rag.retriever import Retriever


class RetrieverTest(unittest.TestCase):
    def setUp(self):
        self.embedder = Mock()
        self.embedder.gerar_embedding.return_value = [1.0, 0.0]
        self.store = Mock()
        self.store.buscar_hibridos.return_value = self.store.buscar_similares.return_value = [{
            "chunk_id": "abc", "conteudo": "Árvore AVL", "periodo": "03",
            "disciplina": "estrutura_de_dados_avancada", "assunto": "avl",
            "arquivo": "Aula_2.pdf", "pagina": 84, "tipo_arquivo": "pdf",
            "tipo_extracao": "textual", "similaridade": 0.8,
            "metadata": {"paginas_mescladas": [83], "campo_extra": "mantido"},
        }]
        self.retriever = Retriever(self.embedder, self.store)

    def test_encaminha_filtros_e_preserva_metadados(self):
        resultados = self.retriever.recuperar(
            " O que é AVL? ", "estrutura_de_dados_avancada", " avl ", k=3
        )
        self.embedder.gerar_embedding.assert_called_once_with("O que é AVL?")
        self.store.buscar_hibridos.assert_called_once_with(
            [1.0, 0.0], "O que é AVL?", "estrutura_de_dados_avancada", assunto="avl", k=3
        )
        self.assertEqual(resultados[0]["metadata"]["paginas_mescladas"], [83])
        self.assertEqual(resultados[0]["metadata"]["campo_extra"], "mantido")
        self.assertEqual(resultados[0]["metadata"]["tipo_arquivo"], "pdf")

    def test_rejeita_entrada_antes_de_consultar_banco(self):
        for pergunta, disciplina, assunto, k in [
            (" ", "ed", None, 3), ("AVL?", " ", None, 3),
            ("AVL?", "ed", " ", 3), ("AVL?", "ed", None, True),
            ("AVL?", "ed", None, 0), ("AVL?", "ed", None, 51),
        ]:
            with self.subTest((pergunta, disciplina, assunto, k)):
                with self.assertRaises(ValueError):
                    self.retriever.recuperar(pergunta, disciplina, assunto, k)
        self.embedder.gerar_embedding.assert_not_called()
        self.store.buscar_similares.assert_not_called()

    def test_busca_vazia(self):
        self.store.buscar_similares.return_value = []
        self.assertEqual(self.retriever.recuperar("AVL?", "ed"), [])

    def test_colunas_futuras_nulas_nao_apagam_metadados_preservados(self):
        linha = self.store.buscar_similares.return_value[0]
        linha.update(tipo_material=None, titulo_material=None, material_id=None)
        linha["metadata"].update(tipo_material="SLIDE_AULA", titulo_material="Slides", material_id=12)
        m = self.retriever.recuperar("AVL?", "estrutura_de_dados_avancada")[0]["metadata"]
        self.assertEqual(m["tipo_material"], "SLIDE_AULA")
        self.assertEqual(m["titulo_material"], "Slides")
        self.assertEqual(m["material_id"], 12)


if __name__ == "__main__":
    unittest.main()
