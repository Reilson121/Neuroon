import unittest
from unittest.mock import Mock

from app.rag.retriever import Retriever
from scripts.validar_ideacao import conceitos_ausentes, contexto_util
from app.rag.ideacao_search import expandir_siglas, ordenar_evidencias


class IdeacaoSearchTest(unittest.TestCase):
    def test_contexto_focado_recusa_qualidades_como_equivalentes_a_pilares(self):
        linhas = [
            {"chunk_id": "pilares", "conteudo": "Os três pilares da concepção de produto: usuário, negócio e tecnologia.", "similaridade": .8},
            {"chunk_id": "qualidades", "conteudo": "Uma solução deve ser desejável, viável e útil.", "similaridade": .7},
        ]
        resultado = ordenar_evidencias(linhas, "Quais são os três pilares da concepção de produto?", 5)
        self.assertEqual([c["chunk_id"] for c in resultado], ["pilares"])

    def test_contexto_focado_preserva_paginas_complementares(self):
        linhas = [
            {"chunk_id": "31", "conteudo": "Etapas do UCD: compreender, definir, prototipar.", "similaridade": .57},
            {"chunk_id": "32", "conteudo": "Etapas do UCD: testar, refinar, implementar.", "similaridade": .54},
        ]
        self.assertEqual(len(ordenar_evidencias(linhas, "Etapas do Design Centrado no Usuário?", 5)), 2)

    def test_validador_aceita_evidencia_literal_e_recusa_contexto_sem_apoio(self):
        self.assertTrue(contexto_util({"similaridade": .19, "cobertura_lexical": .8}))
        self.assertFalse(contexto_util({"similaridade": .19, "cobertura_lexical": .1}))

    def test_termo_raro_nao_e_ocultado_por_slides_genericos(self):
        linhas = [{"chunk_id": str(i), "conteudo": "Métricas-chave e resultados do produto.",
                   "similaridade": .9 - i * .01} for i in range(10)]
        linhas.append({"chunk_id": "definicao", "conteudo": "Métricas de vaidade parecem positivas, mas não demonstram valor real.",
                       "similaridade": .4})
        resultado = ordenar_evidencias(linhas, "Qual a diferença entre métricas de vaidade e métricas relevantes?", 5)
        self.assertEqual(resultado[0]["chunk_id"], "definicao")
        self.assertEqual(resultado[0]["similaridade"], .4)

    def test_proposta_unica_e_sigla_usam_o_mesmo_conceito_do_slide(self):
        self.assertEqual(expandir_siglas("Como estruturar a proposta única de valor no Lean Canvas?"), "proposta valor")
        self.assertEqual(expandir_siglas("Como estruturar a PUV?"), "proposta valor")
        self.assertEqual(expandir_siglas("Quais são os blocos do Lean Canvas?"), "Quais são os blocos do Lean Canvas?")

    def test_lista_removida_pelo_verificador_nao_passa_por_resposta_completa(self):
        resposta = "A técnica SCAMPER é composta pelas seguintes ações [F1]."
        self.assertEqual(len(conceitos_ausentes("scamper", resposta)), 7)
        self.assertEqual(conceitos_ausentes("scamper", "Substituir, combinar, adaptar, modificar, propor para outro uso, eliminar e reverter."), [])

    def test_busca_lexical_inclui_sigla_mas_preserva_embedding_pergunta_e_fontes(self):
        embedder, store = Mock(), Mock()
        embedder.gerar_embedding.return_value = [1, 0]
        store.buscar_hibridos.return_value = [{
            "chunk_id": "ucd", "conteudo": "Etapas do UCD", "similaridade": .4,
            "disciplina": "projeto_de_ideacao_de_software", "assunto": "introducao",
            "arquivo": "Aula 01.pdf", "pagina": 31, "metadata": {},
        }]
        pergunta = "Quais são as etapas do Design Centrado no Usuário?"
        resultado = Retriever(embedder, store).recuperar(pergunta, "projeto_de_ideacao_de_software", "introducao")
        embedder.gerar_embedding.assert_called_once_with(pergunta)
        store.buscar_hibridos.assert_called_once_with(
            [1, 0], "UCD", "projeto_de_ideacao_de_software", assunto="introducao", k=50)
        store.buscar_similares.assert_not_called()
        self.assertEqual(resultado[0]["metadata"]["pagina"], 31)
        self.assertEqual(resultado[0]["conteudo"], "Etapas do UCD")

    def test_estrutura_de_dados_usa_hibrida_sem_expansao_de_siglas_de_ideacao(self):
        embedder, store = Mock(), Mock()
        embedder.gerar_embedding.return_value = [1, 0]
        store.buscar_hibridos.return_value = []
        Retriever(embedder, store).recuperar("Rotação AVL?", "estrutura_de_dados_avancada")
        store.buscar_similares.assert_not_called()
        store.buscar_hibridos.assert_called_once_with([1, 0], "Rotação AVL? rotacoes", "estrutura_de_dados_avancada", assunto=None, k=5)


if __name__ == "__main__":
    unittest.main()
