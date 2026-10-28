import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

class StartupTests(unittest.TestCase):
    @patch('app.api.chat.obter_monitor')
    def test_pre_carregamento_opcional_usa_monitor_existente(self,monitor):
        with patch.dict(os.environ,{'NEURON_PRELOAD_MONITOR':'1'}):
            with TestClient(app) as c:
                self.assertEqual(c.get('/health').status_code,200)
                monitor.assert_called_once_with()

    @patch('app.api.chat.obter_monitor')
    def test_health_sem_pre_carregamento_nao_exige_rag(self,monitor):
        with patch.dict(os.environ,{'NEURON_PRELOAD_MONITOR':'0'}):
            with TestClient(app) as c:self.assertEqual(c.get('/health').status_code,200)
        monitor.assert_not_called()
