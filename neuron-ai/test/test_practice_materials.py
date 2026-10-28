import copy
import json
import unittest
from unittest.mock import Mock,MagicMock
from app.practice.material_index import PROPOSTAS,preparar
from app.practice.repository import QuestionRepository
from app.practice.originals import preparar_original
from app.rag.mapas.estatistica import ORDEM_ASSUNTOS

class PracticeMaterialsTests(unittest.TestCase):
    def setUp(self):
        self.inv=json.loads((PROPOSTAS/'inventario.json').read_text(encoding='utf-8'))
        self.assuntos={s:{'id':i+1,'ativo':True,'disciplina_id':1} for i,s in enumerate(ORDEM_ASSUNTOS)}
    def material(self,r,i):
        return {'id':i,'disciplina_id':1,'periodo_id':1,'ativo':True,'disciplina_ativa':True,'periodo_ativo':True,'possui_prova':True,
                'titulo':r['arquivo_original'],'tipo':r['tipo_material_proposto'],'fonte_monitor_virtual':r['tipo_material_proposto']=='SLIDE_AULA',
                'autorizacao_professor':True,'disponivel_para_pratica':True,
                'referencia_externa':'local:materiais_academicos/periodo_03/estatistica/'+r['arquivo_original']}
    def test_preserva_questao_inteira_origens_e_pagina_docx_desconhecida(self):
        chunks=[]
        for i,r in enumerate(self.inv['arquivos']):
            if r['tipo_material_proposto'] in {'LISTA_EXERCICIOS','PROVA_ANTIGA'}:
                m=self.material(r,i+1)
                saida=preparar(m,self.assuntos,self.inv)
                self.assertEqual(saida,preparar(m,self.assuntos,self.inv));chunks.extend(saida)
        self.assertEqual(len(chunks),15);self.assertEqual(len({json.loads(c['conteudo'])['referencia_local'] for c in chunks}),9)
        self.assertEqual(len({c['chunk_id'] for c in chunks}),15)
        for c in chunks:
            q=json.loads(c['conteudo']);meta=c['metadata']
            self.assertIn('enunciado',q);self.assertTrue(meta['numero_questao'])
            self.assertLessEqual(len(meta['tipo_extracao']),20)
            self.assertIn(meta['tipo_extracao'],{'textual','multimodal'})
            self.assertTrue(meta['transcricao_conferida'])
            if meta['tipo_arquivo']=='docx':self.assertIsNone(meta['pagina'])
            if q['formato_original']!='multipla_escolha':self.assertTrue(q.get('subitens') or q.get('enunciado'))
    def test_recusa_material_sem_autorizacao_e_assunto_inativo(self):
        r=next(r for r in self.inv['arquivos'] if r['tipo_material_proposto']=='LISTA_EXERCICIOS')
        m=self.material(r,2);m['autorizacao_professor']=False
        with self.assertRaises(ValueError):preparar(m,self.assuntos,self.inv)
        m['autorizacao_professor']=True;self.assuntos['medidas_de_dispersao_e_posicao']['ativo']=False
        with self.assertRaises(ValueError):preparar(m,self.assuntos,self.inv)
    def test_vinculo_dos_slides_preserva_titulo_e_metadados_originais(self):
        from app.rag.estatistica_corpus import carregar_validado
        original=carregar_validado()['chunks']
        r=next(r for r in self.inv['arquivos'] if r['tipo_material_proposto']=='SLIDE_AULA')
        saida=preparar(self.material(r,1),self.assuntos,self.inv)
        self.assertEqual(len(saida),193)
        for antes,depois in zip(original,saida):
            self.assertEqual(antes['conteudo'],depois['conteudo'])
            self.assertEqual(antes['metadata']['titulo_material'],depois['metadata']['titulo_material'])
            self.assertEqual(depois['metadata']['titulo_cadastro_material'],r['arquivo_original'])
            self.assertEqual(depois['metadata']['material_id'],1)
    def test_revogar_origem_do_gabarito_remove_resposta_da_lista(self):
        q=json.loads((PROPOSTAS/'avaliacoes_preparadas.json').read_text(encoding='utf-8'))['questoes'][0]
        metadata={'numero_questao':'1','assunto_id':6,'assunto_ids':[6]}
        linha={'conteudo':json.dumps(q),'metadata':metadata,'material_id':3,'titulo':'Prova',
               'arquivo':'prova anterior de estátisitica.pdf','pagina':1,'disciplina_slug':'estatistica'}
        store=MagicMock();con=MagicMock();cur=MagicMock();store._conectar.return_value.__enter__.return_value=con
        con.cursor.return_value.__enter__.return_value=cur;cur.fetchall.return_value=[linha]
        refs=QuestionRepository(store).buscar_questoes(1,None,[3],'PROVA')
        self.assertIsNone(refs[0]['gabarito_material'])
        correcao=preparar_original(refs[0]);self.assertEqual(correcao['gabarito'],'B')
        self.assertEqual(correcao['origem_gabarito'],'GERADO_IA_NAO_OFICIAL')
        self.assertIn('precisa ser conferida',correcao['aviso'])
