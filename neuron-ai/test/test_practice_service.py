import copy
import json
import unittest
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

from app.practice.service import PracticeService, PracticeError


def referencias():
    base=Path(__file__).resolve().parents[1]
    qs=json.loads((base/'propostas/estatistica/avaliacoes_preparadas.json').read_text(encoding='utf-8'))['questoes']
    result=[]
    for q in qs:
        q=copy.deepcopy(q)
        a=10 if q['assunto_principal_proposto']=='medidas_de_dispersao_e_posicao' else 11
        q.update(fontes=[{'material_id':2,'titulo_material':'Prova','arquivo':'prova.pdf','pagina':1,'numero_questao':q['referencia_local'][-2:]}],assunto_id=a,assunto_ids=[a],assuntos_por_id={str(a):q['assunto_principal_proposto']})
        result.append(q)
    return result


class PracticeServiceTests(unittest.TestCase):
    def setUp(self):
        self.repo=Mock();self.repo.buscar_questoes.return_value=referencias()
        self.narrar=Mock(side_effect=lambda qs:['Uma equipe analisa registros para planejar melhorias.' for _ in qs])
        self.service=PracticeService(repository=self.repo,narrador=self.narrar)
        self.req={'sessao_id':str(uuid.uuid4()),'usuario_id':1,'disciplina_id':3,'assunto_id':None,'material_ids':[2],'origem':'MISTO','modo':'CADASTRADAS','quantidade':10,'excluir_fingerprints':[]}

    def test_originais_preservados_sem_expor_gabarito(self):
        r=self.service.montar_questoes(self.req)
        self.assertEqual(len(r['questoes']),6)
        for q in r['questoes']:
            self.assertEqual(q['origem'],'MATERIAL_ACADEMICO')
            self.assertNotIn('gabarito',q)
            self.assertNotIn('resolucao',q)
            self.assertNotIn('spec',q)
        self.narrar.assert_not_called()

    def test_estado_vazio_nao_gera_para_preencher(self):
        self.repo.buscar_questoes.return_value=[]
        self.req['modo']='GERADAS_IA'
        self.assertEqual(self.service.montar_questoes(self.req),{'questoes':[]})
        self.narrar.assert_not_called()

    def test_filtra_assunto_e_rejeita_material_inesperado(self):
        self.req['assunto_id']=10
        r=self.service.montar_questoes(self.req)
        self.assertEqual(len(r['questoes']),2)
        self.repo.buscar_questoes.assert_called_once_with(3,10,[2],'MISTO')
        self.req['sessao_id']=str(uuid.uuid4());self.req['material_ids']=[99]
        with self.assertRaises(ValueError):self.service.montar_questoes(self.req)

    def test_correcao_com_aviso_sem_gabarito_oficial(self):
        self.repo.buscar_questoes.return_value=[referencias()[2]]
        q=self.service.montar_questoes(self.req)['questoes'][0]
        req={'sessao_id':self.req['sessao_id'],'usuario_id':1,'questao_id':q['id'],'alternativa':'A','material_ids':[2]}
        r=self.service.corrigir(req)
        self.assertTrue(r['correto']);self.assertEqual(r['alternativa_correta'],'A')
        self.assertEqual(r['origem_gabarito'],'GERADO_IA_NAO_OFICIAL')
        self.assertIn('precisa ser conferida',r['aviso'])
        self.assertEqual(self.service.corrigir(req),r)
        req['alternativa']='B'
        with self.assertRaises(PracticeError) as erro:self.service.corrigir(req)
        self.assertEqual(erro.exception.codigo,'RESPOSTA_JA_REGISTRADA')

    def test_isola_usuario_questao_material_e_expiracao(self):
        q=self.service.montar_questoes(self.req)['questoes'][0]
        req={'sessao_id':self.req['sessao_id'],'usuario_id':2,'questao_id':q['id'],'alternativa':'A','material_ids':[2]}
        with self.assertRaises(PracticeError):self.service.corrigir(req)
        req['usuario_id']=1;req['material_ids']=[]
        with self.assertRaises(PracticeError) as erro:self.service.corrigir(req)
        self.assertEqual(erro.exception.codigo,'MATERIAL_INDISPONIVEL')
        req['material_ids']=[2]
        with patch('app.practice.service.time.monotonic',return_value=10**15):
            with self.assertRaises(PracticeError):self.service.corrigir(req)

    def test_geradas_tem_calculo_verificado_e_contexto_em_lote(self):
        self.req.update(modo='GERADAS_IA',quantidade=6)
        qs=self.service.montar_questoes(self.req)['questoes']
        self.assertEqual(len(qs),6)
        self.narrar.assert_called_once()
        for q in qs:
            self.assertEqual(q['origem'],'GERADA_IA')
            self.assertNotIn('gabarito',q)
            self.assertIn('Questão inédita',q['aviso'])
        self.assertGreater(len({q['conceito'] for q in qs}),1)

    def test_exclui_questoes_vistas_sem_inventar_ou_repetir(self):
        self.req['excluir_fingerprints']=[q['referencia_local'] for q in referencias()]
        self.assertEqual(self.service.montar_questoes(self.req),{'questoes':[]})


if __name__=='__main__':unittest.main()
