import copy
import json
import tempfile
import unittest
from pathlib import Path

from app.rag.ideacao_corpus import (
    AULAS, DISCIPLINA, RAIZ, REVISOES, carregar_validado, consolidar, sha256, validar_aula,
)
from scripts.validar_ideacao import conferir_fontes


class IdeacaoCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = carregar_validado()

    def test_cinco_aulas_todas_paginas_com_fontes_e_ids_unicos(self):
        dados = self.dados
        self.assertEqual(dados["total_paginas"], 180)
        self.assertEqual({a["aula"] for a in dados["arquivos"]}, set(AULAS))
        paginas = {(p["metadata"]["aula"], p["metadata"]["pagina"]) for p in dados["paginas"]}
        fontes = {(c["metadata"]["aula"], c["metadata"]["pagina"]) for c in dados["chunks"]}
        self.assertEqual(paginas, fontes)
        self.assertEqual(len(paginas), 180)
        self.assertEqual(len({c["chunk_id"] for c in dados["chunks"]}), len(dados["chunks"]))
        self.assertTrue(all(c["metadata"]["disciplina"] == DISCIPLINA for c in dados["chunks"]))
        self.assertNotIn("\x00", "".join(p["conteudo"] for p in dados["paginas"]))

    def test_reprocessamento_local_preserva_fontes_e_resultado(self):
        caminhos = [RAIZ / a["json_origem"] for a in self.dados["arquivos"]]
        antes = [sha256(p.read_bytes()) for p in caminhos]
        self.assertEqual(consolidar(), self.dados)
        self.assertEqual(antes, [sha256(p.read_bytes()) for p in caminhos])

    def test_rejeita_paginas_ausentes_duplicadas_vazias_e_outra_origem(self):
        a = self.dados["arquivos"][0]
        origem = json.loads((RAIZ / a["json_origem"]).read_text(encoding="utf-8"))
        for mutacao in ("ausente", "duplicada", "vazia", "disciplina", "arquivo", "hash"):
            dados = copy.deepcopy(origem)
            if mutacao == "ausente":
                dados["paginas"].pop()
            elif mutacao == "duplicada":
                dados["paginas"][1] = copy.deepcopy(dados["paginas"][0])
            elif mutacao == "vazia":
                dados["paginas"][0]["conteudo"] = " "
            elif mutacao in {"disciplina", "arquivo"}:
                dados["paginas"][0]["metadata"][mutacao] = "outra_origem"
            else:
                dados["resumo"]["pdf_sha256"] = "outro_hash"
            with self.subTest(mutacao=mutacao), self.assertRaises(ValueError):
                validar_aula(dados, "01", a["arquivo"], a["paginas"], a["pdf_sha256"])

    def test_rejeita_revisao_de_pdf_alterado_e_pagina_inexistente(self):
        p = self.dados["paginas"][0]
        correcao = {"aula": "01", "pagina": 1, "pdf_sha256": "hash_invalido",
                    "conteudo_anterior_sha256": sha256(p["conteudo"].encode()),
                    "conteudo": "correção", "motivo": "teste"}
        with tempfile.TemporaryDirectory(dir=RAIZ / "tmp") as pasta:
            destino = Path(pasta) / "revisoes.json"
            for pagina in (1, 999):
                correcao["pagina"] = pagina
                destino.write_text(json.dumps({"paginas": [correcao]}), encoding="utf-8")
                with self.subTest(pagina=pagina), self.assertRaises(ValueError):
                    consolidar(revisoes_path=destino)

    def test_quadros_visuais_de_historias_nao_se_limitam_ao_titulo(self):
        paginas = {p["metadata"]["pagina"]: p for p in self.dados["paginas"]
                   if p["metadata"]["aula"] == "03"}
        for n in (3, 4):
            self.assertEqual(paginas[n]["metadata"]["tipo_extracao"], "multimodal")
            self.assertGreater(len(paginas[n]["conteudo"]), 180)
        self.assertIn("objetivo", paginas[3]["conteudo"].lower())
        self.assertIn("prioriza", paginas[4]["conteudo"].lower())

    def test_validador_recusa_fonte_alterada_e_filtro_de_outra_aula(self):
        chunk = self.dados["chunks"][0]
        origem = {chunk["chunk_id"]: chunk}
        item = copy.deepcopy(chunk)
        self.assertTrue(conferir_fontes([item], origem, trechos=True))
        self.assertFalse(conferir_fontes([item], origem, "lean_canvas", trechos=True))
        item["conteudo"] += " texto estranho"
        self.assertFalse(conferir_fontes([item], origem, trechos=True))


if __name__ == "__main__":
    unittest.main()
