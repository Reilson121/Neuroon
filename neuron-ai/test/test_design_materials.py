import copy
import unittest
from unittest.mock import patch
from app.rag.design_corpus import carregar_validado, preparar_material, DISCIPLINA


class DesignMaterialsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = carregar_validado()

    def setUp(self):
        self.assuntos = {a['assunto']: dict(id=i+1, ativo=True, disciplina_id=42)
                         for i, a in enumerate(self.corpus['arquivos'])}
        self.material = dict(id=8, disciplina_id=42, disciplina_slug=DISCIPLINA,
            periodo_id=3, periodo_numero=3, assunto_id=1, titulo='Aula 1',
            tipo='SLIDE_AULA', ativo=True, disciplina_ativa=True, periodo_ativo=True,
            fonte_monitor_virtual=True, autorizacao_professor=False,
            referencia_externa='local:' + self.corpus['arquivos'][0]['pdf'])
        self.mock = patch('app.rag.design_corpus.carregar_validado', return_value=self.corpus)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def test_vincula_363_chunks_sem_alterar_conteudo_ou_proveniencia(self):
        antes = copy.deepcopy(self.corpus)
        saida = []
        for i, a in enumerate(self.corpus['arquivos']):
            material = {**self.material, 'id': 8+i, 'assunto_id': i+1,
                        'referencia_externa': 'local:' + a['pdf']}
            chunks = preparar_material(material, self.assuntos)
            self.assertEqual(len(chunks), a['chunks'])
            self.assertTrue(all(c['metadata']['material_id'] == 8+i
                                and c['metadata']['assunto_id'] == i+1 for c in chunks))
            saida.extend(chunks)
        self.assertEqual(len(saida), 363)
        por_id = {c['chunk_id']: c for c in saida}
        for c in self.corpus['chunks']:
            novo = por_id[c['chunk_id']]
            self.assertEqual(novo['conteudo'], c['conteudo'])
            self.assertFalse(novo['metadata']['disponivel_para_pratica'])
            for k, v in c['metadata'].items():
                self.assertEqual(novo['metadata'][k], v)
        self.assertEqual(self.corpus, antes)

    def test_recusa_contexto_revogado_e_origem_incompativel(self):
        casos = [{k: False} for k in ('ativo','disciplina_ativa','periodo_ativo','fonte_monitor_virtual')]
        casos += [dict(referencia_externa='local:../fora.pdf'), dict(tipo='PROVA_ANTIGA'),
                  dict(disciplina_slug='estatistica'), dict(periodo_numero=2), dict(assunto_id=999)]
        for mudanca in casos:
            with self.subTest(mudanca=mudanca), self.assertRaises(ValueError):
                preparar_material({**self.material, **mudanca}, self.assuntos)

    def test_recusa_assunto_inativo_ou_de_outra_disciplina(self):
        for mudanca in (dict(ativo=False), dict(disciplina_id=99)):
            assuntos = copy.deepcopy(self.assuntos)
            assuntos['introducao_ao_design'].update(mudanca)
            with self.assertRaises(ValueError):
                preparar_material(self.material, assuntos)
