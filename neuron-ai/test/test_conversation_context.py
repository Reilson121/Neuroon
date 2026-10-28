import json
import unittest
from unittest.mock import Mock
from app.rag.monitor_virtual import MonitorVirtual
from app.rag.conversation_context import ContextoConversa


class ConversationContextTests(unittest.TestCase):
    def setUp(self):
        self.historico = [{'papel':'USUARIO','conteudo':'O que são pilhas?'},
                          {'papel':'MONITOR','conteudo':'Segue o princípio LIFO. [F9]'}]
        self.retriever = Mock()
        self.retriever.recuperar.return_value = [{'chunk_id':'pilhas','conteudo':'PILHAS: último a entrar, primeiro a sair.',
            'similaridade':.8,'metadata':{'arquivo':'Aula_0.pdf','pagina':14}}]
        self.gerar = Mock(return_value=json.dumps({'suficiente':True,'resposta':'Exemplo didático criado pela IA: pense numa pilha de pratos, retirando primeiro o último colocado. [F1]',
            'visuais':[{'markdown':'```text\nTOPO -> C\n        B\n        A\n```','fontes':['F1']}]}))
        self.contextualizar = Mock(return_value='{"consulta":"pilhas LIFO"}')

    def monitor(self):
        return MonitorVirtual(self.retriever,self.gerar,gerar_contexto=self.contextualizar)

    def test_continuidade_funciona_no_componente_compartilhado_das_quatro_disciplinas(self):
        for disciplina in ('estrutura_de_dados_avancada','estatistica','design_de_artefatos_digitais','projeto_de_ideacao_de_software'):
            with self.subTest(disciplina=disciplina):
                self.retriever.reset_mock()
                r=self.monitor().responder('Pode explicar de forma mais didática e visual?',disciplina,'assunto_selecionado',historico=self.historico)
                self.assertFalse(r['fallback'])
                self.retriever.recuperar.assert_called_once_with('pilhas LIFO',disciplina,'assunto_selecionado',k=5)
                prompt=self.gerar.call_args.args[0].to_messages()[-1].content
                self.assertIn('Pode explicar de forma mais didática e visual?',prompt)
                self.assertIn('O que são pilhas?',prompt)
                self.assertEqual(r['fontes'][0]['pagina'],14)

    def test_nova_pergunta_independente_mantem_novo_tema_e_nao_mistura_requisicoes(self):
        m=self.monitor()
        self.contextualizar.return_value='{"consulta":"filas FIFO"}'
        m.responder('E o que são filas?','ed',historico=self.historico)
        self.assertEqual(self.retriever.recuperar.call_args.args[0],'filas FIFO')
        self.contextualizar.reset_mock();self.retriever.reset_mock()
        m.responder('O que é AVL?','ed')
        self.contextualizar.assert_not_called()
        self.retriever.recuperar.assert_called_once_with('O que é AVL?','ed',None,k=5)
        self.assertNotIn('O que são pilhas?',self.gerar.call_args.args[0].to_messages()[-1].content)

    def test_historico_nao_substitui_material_revogado_ou_sem_contexto(self):
        self.retriever.recuperar.return_value=[]
        r=self.monitor().responder('Explique melhor','ed',historico=self.historico)
        self.assertTrue(r['fallback']);self.assertEqual(r['fontes'],[])
        self.gerar.assert_not_called()

    def test_ambiguidade_pede_tema_e_saida_invalida_nao_vira_busca(self):
        for bruto,motivo in [('{"consulta":null}','tema_nao_identificado'),('texto livre','formato_invalido'),
                              ('{"consulta":"pilhas","extra":true}','formato_invalido')]:
            with self.subTest(bruto=bruto):
                self.contextualizar.return_value=bruto;self.retriever.reset_mock()
                r=self.monitor().responder('Explique melhor','ed',historico=self.historico)
                self.assertEqual(r['motivo'],motivo);self.retriever.recuperar.assert_not_called()

    def test_diagrama_com_linhas_vazias_e_citacao_externa_e_preservado(self):
        resposta='Exemplo didático criado pela IA. [F1]\n\n```text\nTOPO -> C\n\n        B\n        A\n```\n\n[F1]'
        r=MonitorVirtual._interpretar_resposta(json.dumps({'suficiente':True,'resposta':resposta}),{'F1':{'pagina':14}})
        self.assertFalse(r['fallback']);self.assertIn('TOPO -> C\n\n        B',r['resposta'])
        self.assertEqual(r['blocos_sem_fonte_removidos'],0)
        invalida=MonitorVirtual._interpretar_resposta(json.dumps({'suficiente':True,'resposta':resposta.replace('[F1]','[F99]')}),{'F1':{}})
        self.assertEqual(invalida['motivo'],'fontes_invalidas')

    def test_diagrama_sem_fonte_continua_descartado(self):
        r=MonitorVirtual._interpretar_resposta(json.dumps({'suficiente':True,'resposta':'Conceito. [F1]\n\n```text\nexemplo sem fonte\n```'}),{'F1':{}})
        self.assertNotIn('exemplo sem fonte',r['resposta'])

    def test_rotulo_citado_pelo_modelo_mantem_seu_proprio_exemplo(self):
        texto='Exemplo didático criado pela IA com o conceito em [F1].\n\n```text\nTOPO -> C\n        B\n        A\n```'
        r=MonitorVirtual._interpretar_resposta(json.dumps({'suficiente':True,'resposta':texto}),{'F1':{'pagina':14}})
        self.assertIn('TOPO -> C',r['resposta'])
        self.assertEqual(r['blocos_sem_fonte_removidos'],0)

    def test_tabela_didatica_com_legenda_citada_nao_e_descartada(self):
        texto='Exemplo didático criado pela IA, baseado em [F1].\n\n| Etapa | Pilha |\n| --- | --- |\n| Colocar A | A |\n| Colocar B | B, A |'
        r=MonitorVirtual._interpretar_resposta(json.dumps({'suficiente':True,'resposta':texto}),{'F1':{}})
        self.assertIn('| Colocar B |',r['resposta'])

    def test_visual_estruturado_tem_citacao_explicita_do_modelo_sem_inventar_fontes(self):
        dados={'suficiente':True,'resposta':'Uma pilha segue LIFO. [F1]',
               'visuais':[{'markdown':'```text\nTOPO -> C\n        B\n        A\n```','fontes':['F1']}]}
        r=MonitorVirtual._interpretar_resposta(json.dumps(dados),{'F1':{'pagina':14}})
        self.assertFalse(r['fallback']);self.assertIn('TOPO -> C',r['resposta'])
        self.assertIn('criado pela IA',r['resposta']);self.assertEqual(r['fontes'],[{'pagina':14}])
        dados['visuais'][0]['fontes']=['F99']
        self.assertEqual(MonitorVirtual._interpretar_resposta(json.dumps(dados),{'F1':{}})['motivo'],'fontes_invalidas')

    def test_pedido_visual_sem_esquema_tem_um_unico_reparo_com_as_mesmas_fontes(self):
        sem_visual=json.dumps({'suficiente':True,'resposta':'Uma pilha segue LIFO. [F1]'})
        self.gerar.side_effect=[sem_visual,json.dumps({'suficiente':True,'resposta':'Segue LIFO. [F1]',
            'visuais':[{'markdown':'```text\nTOPO -> C\n        B\n```','fontes':['F1']}]})]
        m=self.monitor()
        r=m.responder('Pode explicar de forma visual?','ed',historico=self.historico)
        self.assertFalse(r['fallback']);self.assertIn('TOPO -> C',r['resposta'])
        self.assertEqual(self.gerar.call_count,2);self.retriever.recuperar.assert_called_once()
        self.assertIn('A tentativa anterior omitiu o visual solicitado',self.gerar.call_args.args[0].to_messages()[-1].content)
        self.gerar.reset_mock();self.gerar.side_effect=[sem_visual,sem_visual]
        self.assertEqual(m.responder('Mais visual?','ed',historico=self.historico)['motivo'],'formato_invalido')
        self.assertEqual(self.gerar.call_count,2)
