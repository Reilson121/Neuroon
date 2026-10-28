import copy
import unittest
from app.rag.ed_avancada_corpus import carregar_validado, preparar_material, PREFIXO
from app.rag.mapas.estrutura_de_dados_avancada import MAPA


class EdAvancadaCorpusTests(unittest.TestCase):
    def setUp(self):
        slugs = [s for a in MAPA['arquivos'].values() for s in a['assuntos']]
        self.assuntos = {s: {'id': i+1, 'disciplina_id': 42, 'ativo': True} for i, s in enumerate(slugs)}
        self.material = dict(id=7, disciplina_id=42, periodo_id=3, titulo='Aula 0',
            referencia_externa=PREFIXO+'Aula_0.pdf', tipo='SLIDE_AULA', ativo=True,
            disciplina_ativa=True, periodo_ativo=True, fonte_monitor_virtual=True,
            autorizacao_professor=False)

    def test_preserva_textos_ids_paginas_e_vincula_167_chunks_14_assuntos(self):
        original = carregar_validado()['chunks']
        antes = copy.deepcopy(original)
        saida = []
        for i, arquivo in enumerate(MAPA['arquivos']):
            m = {**self.material, 'id': 7+i, 'referencia_externa': PREFIXO+arquivo}
            chunks = preparar_material(m, self.assuntos)
            self.assertTrue(chunks)
            for c in chunks:
                self.assertEqual(c['metadata']['material_id'], 7+i)
                self.assertEqual(c['metadata']['arquivo'], arquivo)
                self.assertFalse(c['metadata']['disponivel_para_pratica'])
            saida.extend(chunks)
        self.assertEqual(len(saida), 167)
        self.assertEqual(len({c['metadata']['assunto_id'] for c in saida}), 14)
        por_id = {c['chunk_id']: c for c in saida}
        for c in original:
            self.assertEqual(c['conteudo'], por_id[c['chunk_id']]['conteudo'])
            for campo in ('pagina', 'paginas_mescladas', 'assunto', 'aula'):
                self.assertEqual(c['metadata'].get(campo), por_id[c['chunk_id']]['metadata'].get(campo))
        self.assertEqual(original, antes)

    def test_bloqueia_fonte_revogada_contexto_inativo_e_caminho_arbitrario(self):
        for campo in ('ativo', 'disciplina_ativa', 'periodo_ativo', 'fonte_monitor_virtual'):
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                preparar_material({**self.material, campo: False}, self.assuntos)
        for ref in (PREFIXO+'../Aula_0.pdf', 'https://exemplo.com/Aula_0.pdf', PREFIXO+'Aula_99.pdf'):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                preparar_material({**self.material, 'referencia_externa': ref}, self.assuntos)

    def test_bloqueia_assunto_de_outra_disciplina_ou_inativo(self):
        for alteracao in ({'ativo': False}, {'disciplina_id': 99}):
            assuntos = copy.deepcopy(self.assuntos)
            assuntos['conceitos_de_arvores'].update(alteracao)
            with self.assertRaises(ValueError):
                preparar_material(self.material, assuntos)
