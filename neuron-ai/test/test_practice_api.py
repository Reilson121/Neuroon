import os
import unittest
from unittest.mock import patch,Mock
from fastapi.testclient import TestClient
from app.main import app

class PracticeApiTest(unittest.TestCase):
    def test_rotas_internas_exigem_token_e_nao_refletem_segredos(self):
        with patch.dict(os.environ,{'NEURON_INTERNAL_TOKEN':'token-interno-exclusivo-teste'}):
            c=TestClient(app)
            for path in ['/internal/v1/chat','/internal/v1/practice/questions','/internal/v1/materials/index']:
                self.assertEqual(c.post(path,json={}).status_code,401)
                r=c.post(path,json={'campo_extra':'SENTINELA_PRIVADA'},headers={'X-Internal-Token':'token-interno-exclusivo-teste'})
                self.assertEqual(r.status_code,422)
                self.assertNotIn('SENTINELA_PRIVADA',r.text)

    def test_estado_vazio_e_sanitizacao(self):
        req={'sessao_id':'00000000-0000-0000-0000-000000000001','usuario_id':1,'disciplina_id':1,'quantidade':5,'material_ids':[]}
        with patch.dict(os.environ,{'NEURON_INTERNAL_TOKEN':'teste'}),patch('app.api.practice.obter_service') as p:
            p.return_value.montar_questoes.return_value={'questoes':[]}
            c=TestClient(app,headers={'X-Internal-Token':'teste'})
            self.assertEqual(c.post('/internal/v1/practice/questions',json=req).json(),{'questoes':[]})
            p.return_value.montar_questoes.side_effect=RuntimeError('SENTINELA_PRIVADA')
            r=c.post('/internal/v1/practice/questions',json=req)
            self.assertEqual(r.status_code,503);self.assertNotIn('SENTINELA_PRIVADA',r.text)
