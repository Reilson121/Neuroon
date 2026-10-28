"""Integridade da disciplina; não chama modelos nem banco."""

import copy
import json
import unittest

import pymupdf

from app.rag.assunto_processor import AssuntoProcessor
from app.rag.chunk_processor import ChunkProcessor
from app.rag.estatistica_corpus import (
    ARQUIVO, DISCIPLINA, MAPA, PDF, PERIODO, RAIZ, REVISOES, enriquecer, sha256, validar_corpus,
)


class EstatisticaCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = MAPA["arquivos"][ARQUIVO]
        with pymupdf.open(PDF) as doc:
            cls.por_pagina = AssuntoProcessor().validar_arquivo(ARQUIVO, config, len(doc))
            paginas = [{"conteudo": f"Conteúdo de verificação da página {n}. Preserva um único assunto e a origem do PDF.",
                        "metadata": {"periodo": PERIODO, "disciplina": DISCIPLINA, "aula": None,
                                     "arquivo": ARQUIVO, "pagina": n, "assunto": assunto,
                                     "tipo_arquivo": "pdf", "tipo_extracao": "multimodal" if n in config["paginas_multimodais"] else "textual"}}
                       for n, assunto in sorted(cls.por_pagina.items())]
            extracoes = json.loads(REVISOES.read_text(encoding="utf-8")).get("extracoes", {})
            for pagina in paginas:
                correcao = extracoes.get(str(pagina["metadata"]["pagina"]))
                if correcao:
                    pagina["conteudo"] = correcao["conteudo"]
            cls.base = enriquecer({"periodo": PERIODO, "disciplina": DISCIPLINA, "paginas": paginas}, doc, sha256(PDF.read_bytes()))

    def test_mapa_corresponde_ao_aprovado(self):
        aprovado = json.loads((RAIZ / "propostas/estatistica/mapa_proposto.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(json.dumps(MAPA)), aprovado)
        self.assertEqual(len(self.por_pagina), 166)
        self.assertEqual(set(range(1, 177)) - self.por_pagina.keys(), {1, 20, 29, 36, 41, 46, 64, 134, 142, 170})

    def test_corpus_completo_e_revisoes_identificadas(self):
        resumo = validar_corpus(self.base)
        self.assertEqual(resumo["assuntos"], 31)
        self.assertEqual(resumo["paginas_cobertas"], 166)
        pagina = next(p for p in self.base["paginas"] if p["metadata"]["pagina"] == 113)
        self.assertIn("Observação de revisão por IA", pagina["conteudo"])
        self.assertNotIn("Observação de revisão por IA", pagina["conteudo_original"])
        self.assertFalse(pagina["metadata"]["revisao_oficial_professor"])

    def test_rejeita_corpus_parcial_e_outro_assunto(self):
        parcial = copy.deepcopy(self.base)
        parcial["paginas"].pop()
        with self.assertRaises(ValueError):
            validar_corpus(parcial)
        outro = copy.deepcopy(self.base)
        outro["paginas"][0]["metadata"]["assunto"] = "regressao_linear_simples_e_multipla"
        with self.assertRaises(ValueError):
            validar_corpus(outro)

    def test_rejeita_mesclagem_entre_assuntos(self):
        dados = copy.deepcopy(self.base)
        dados["paginas"][0]["metadata"]["paginas_mescladas"] = [14]
        with self.assertRaises(ValueError):
            validar_corpus(dados)

    def test_rejeita_prova_e_outros_metadados(self):
        for campo, valor in [("disciplina", "teoria_dos_grafos"), ("tipo_material", "PROVA_ANTIGA"),
                             ("pdf_sha256", "alterado"), ("arquivo", "prova.pdf")]:
            with self.subTest(campo=campo):
                dados = copy.deepcopy(self.base)
                dados["paginas"][0]["metadata"][campo] = valor
                with self.assertRaises(ValueError):
                    validar_corpus(dados)

    def test_rejeita_revisao_trocada_e_chunk_adulterado(self):
        dados = copy.deepcopy(self.base)
        dados["paginas"][0]["conteudo"] += " Resposta inventada."
        with self.assertRaises(ValueError):
            validar_corpus(dados)
        dados = copy.deepcopy(self.base)
        dados["chunks"][0]["metadata"]["assunto"] = "inexistente"
        with self.assertRaises(ValueError):
            validar_corpus(dados)

    def test_revisao_e_idempotente(self):
        dados = copy.deepcopy(self.base)
        with pymupdf.open(PDF) as doc:
            enriquecer(dados, doc, sha256(PDF.read_bytes()))
        self.assertEqual(dados, self.base)


if __name__ == "__main__":
    unittest.main()
