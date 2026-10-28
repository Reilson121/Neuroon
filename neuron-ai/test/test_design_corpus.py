import copy
import unittest

from app.rag.design_corpus import (
    AULAS, DISCIPLINA, RAIZ, carregar_validado, consolidar, validar_aula,
)


class DesignCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = carregar_validado()

    def test_todas_as_aulas_e_paginas_tem_chunks_e_fontes(self):
        dados = self.dados
        self.assertEqual({a["aula"] for a in dados["arquivos"]}, set(AULAS))
        self.assertEqual(dados["total_paginas"], 310)
        paginas = {(p["metadata"]["aula"], p["metadata"]["pagina"]) for p in dados["paginas"]}
        fontes = {(c["metadata"]["aula"], c["metadata"]["pagina"]) for c in dados["chunks"]}
        self.assertEqual(paginas, fontes)
        self.assertEqual(len({c["chunk_id"] for c in dados["chunks"]}), len(dados["chunks"]))
        self.assertTrue(all(c["metadata"]["disciplina"] == DISCIPLINA for c in dados["chunks"]))

    def test_repara_definicoes_visuais_e_retira_conteudo_invisivel(self):
        paginas = {(p["metadata"]["aula"], p["metadata"]["pagina"]): p["conteudo"]
                   for p in self.dados["paginas"]}
        self.assertIn("luminosidade", paginas["07", 24])
        self.assertIn("equidistantes", paginas["07", 31])
        self.assertIn("Prototipação", paginas["08", 10])
        self.assertIn("O que ela escuta?", paginas["08", 31])
        self.assertNotIn("site de reservas", paginas["complementar", 3])
        self.assertNotIn("site de reservas", paginas["complementar", 14])
        self.assertNotIn("\x00", "".join(paginas.values()))
        consumidor = next(p for p in self.dados["paginas"] if p["metadata"]["aula"] == "04"
                          and p["metadata"]["pagina"] == 3)
        self.assertEqual(consumidor["metadata"]["paginas_mescladas"], [2])
        self.assertIn("comportamento do consumidor", consumidor["conteudo"])
        self.assertIn("SOCIAIS", consumidor["conteudo"])

    def test_consolidacao_e_repetivel_e_preserva_jsons_originais(self):
        import hashlib
        caminhos = [RAIZ / a["json_origem"] for a in self.dados["arquivos"]]
        antes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in caminhos]
        self.assertEqual(consolidar(), self.dados)
        self.assertEqual(antes, [hashlib.sha256(p.read_bytes()).hexdigest() for p in caminhos])

    def test_rejeita_paginas_duplicadas_e_metadados_de_outra_disciplina(self):
        import json
        arquivo = self.dados["arquivos"][0]
        origem = json.loads((RAIZ / arquivo["json_origem"]).read_text(encoding="utf-8"))
        for mutacao in ("duplicar", "disciplina", "vazio"):
            dados = copy.deepcopy(origem)
            if mutacao == "duplicar":
                dados["paginas"][1] = copy.deepcopy(dados["paginas"][0])
            elif mutacao == "disciplina":
                dados["paginas"][0]["metadata"]["disciplina"] = "outra"
            else:
                dados["paginas"][0]["conteudo"] = " "
            with self.subTest(mutacao=mutacao), self.assertRaises(ValueError):
                validar_aula(dados, "01", arquivo["assunto"], arquivo["arquivo"], arquivo["paginas"])

    def test_revisao_de_outra_versao_do_pdf_e_recusada(self):
        import json
        import tempfile
        from pathlib import Path
        from app.rag.design_corpus import REVISOES
        revisoes = json.loads(REVISOES.read_text(encoding="utf-8"))
        revisoes["paginas"][0]["pdf_sha256"] = "versao-alterada"
        with tempfile.TemporaryDirectory(dir=RAIZ / "tmp") as pasta:
            destino = Path(pasta) / "revisoes.json"
            destino.write_text(json.dumps(revisoes), encoding="utf-8")
            with self.assertRaises(ValueError):
                consolidar(revisoes_path=destino)


if __name__ == "__main__":
    unittest.main()
