import copy
import unittest

from app.rag.index_audit import comparar_chunks


class IndexAuditTest(unittest.TestCase):
    def setUp(self):
        self.chunks = [{
            "chunk_id": "a", "conteudo": "AVL", "metadata": {
                "arquivo": "Aula_2.pdf", "pagina": 84, "paginas_mescladas": [83],
            },
        }]

    def test_aceita_mesmos_chunks_com_metadados_extras_no_banco(self):
        atuais = copy.deepcopy(self.chunks)
        atuais[0]["metadata"]["material_id"] = None
        self.assertTrue(comparar_chunks(self.chunks, atuais)["compativel"])

    def test_detecta_chunks_antigos_e_ausentes(self):
        atuais = copy.deepcopy(self.chunks)
        atuais[0]["chunk_id"] = "antigo"
        resultado = comparar_chunks(self.chunks, atuais)
        self.assertFalse(resultado["compativel"])
        self.assertEqual(resultado["faltantes"], ["a"])
        self.assertEqual(resultado["extras"], ["antigo"])

    def test_detecta_texto_alterado_com_mesmo_id(self):
        atuais = copy.deepcopy(self.chunks)
        atuais[0]["conteudo"] = "Versão anterior"
        resultado = comparar_chunks(self.chunks, atuais)
        self.assertFalse(resultado["compativel"])
        self.assertEqual(resultado["conteudos_divergentes"], ["a"])

    def test_detecta_perda_de_paginas_mescladas(self):
        atuais = copy.deepcopy(self.chunks)
        del atuais[0]["metadata"]["paginas_mescladas"]
        self.assertEqual(comparar_chunks(self.chunks, atuais)["metadados_divergentes"], ["a"])

    def test_rejeita_ids_duplicados(self):
        with self.assertRaises(ValueError):
            comparar_chunks(self.chunks * 2, self.chunks)


if __name__ == "__main__":
    unittest.main()
