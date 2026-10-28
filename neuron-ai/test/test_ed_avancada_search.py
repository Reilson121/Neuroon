import json
import unittest
from pathlib import Path
from unittest.mock import Mock
from app.rag.ed_avancada_search import expandir_variantes
from app.rag.hybrid_search import ordenar_hibrido
from app.rag.retriever import Retriever
from app.rag.monitor_virtual import MonitorVirtual

ROOT = Path(__file__).resolve().parents[1]


class EdAvancadaSearchTests(unittest.TestCase):
    def test_recupera_slide_de_pilhas_mesmo_com_score_baixo_e_pergunta_no_singular(self):
        chunks = json.loads((ROOT/'saidas_testes/estrutura_de_dados_avancada_aula_0_aula_1_aula_2.json').read_text(encoding='utf-8'))['chunks']
        linhas = [{**c['metadata'], 'metadata': c['metadata'], 'chunk_id': c['chunk_id'],
                   'conteudo': c['conteudo'], 'similaridade': .15 if c['metadata']['pagina'] == 14 else .4}
                  for c in chunks if c['metadata']['assunto'] == 'revisao_estruturas_em_c']
        for pergunta in ('o que uma pilha?', 'o que sao pilhas?', 'O que é uma pilha?'):
            with self.subTest(pergunta=pergunta):
                encontrados = ordenar_hibrido(linhas, expandir_variantes(pergunta), 5)
                pilhas = next(c for c in encontrados if c['pagina'] == 14)
                self.assertEqual(pilhas['similaridade'], .15)
                self.assertGreaterEqual(pilhas['cobertura_lexical'], .5)
                recuperador = Mock()
                recuperador.recuperar.return_value = [pilhas]
                gerar = Mock(return_value=json.dumps({'suficiente': True, 'resposta': 'Segue LIFO: o último a entrar é o primeiro a sair. [F1]'}))
                resposta = MonitorVirtual(recuperador, gerar).responder(pergunta, 'estrutura_de_dados_avancada', 'revisao_estruturas_em_c')
                self.assertFalse(resposta['fallback'])
                self.assertEqual(resposta['fontes'][0]['pagina'], 14)
                gerar.assert_called_once()

    def test_embedding_original_e_filtros_sao_preservados(self):
        embedder, store = Mock(), Mock()
        embedder.gerar_embedding.return_value = [1, 0]
        store.buscar_hibridos.return_value = []
        Retriever(embedder, store).recuperar('o que uma pilha?', 'estrutura_de_dados_avancada', 'revisao_estruturas_em_c')
        embedder.gerar_embedding.assert_called_once_with('o que uma pilha?')
        store.buscar_hibridos.assert_called_once_with([1, 0], 'o que uma pilha? pilhas', 'estrutura_de_dados_avancada', assunto='revisao_estruturas_em_c', k=5)
        store.buscar_similares.assert_not_called()

    def test_pergunta_fora_do_material_nao_ganha_evidencia_lexical(self):
        self.assertEqual(expandir_variantes('Qual é a capital da França?'), 'Qual é a capital da França?')
        linhas = [{'chunk_id': 'pilhas', 'conteudo': 'PILHAS: princípio LIFO.', 'similaridade': .1}]
        resultado = ordenar_hibrido(linhas, expandir_variantes('Qual é a capital da França?'), 5)
        self.assertNotIn('cobertura_lexical', resultado[0])
        recuperador, gerar = Mock(), Mock()
        recuperador.recuperar.return_value = [{**resultado[0], 'metadata': {'arquivo': 'Aula_0.pdf', 'pagina': 14}}]
        self.assertTrue(MonitorVirtual(recuperador, gerar).responder('Qual é a capital da França?', 'estrutura_de_dados_avancada')['fallback'])
        gerar.assert_not_called()
