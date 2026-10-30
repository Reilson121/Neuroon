import copy
import json
import random
import unittest
import uuid
from unittest.mock import Mock,patch
from app.rag.ed_basica_corpus import carregar_validado,consolidar,preparar_material,MATERIAIS
from app.practice.ed_basica_engine import gerar,construir,verificar,preparar_original,contextualizar
from app.practice.ed_basica_bank import BANCOS
from app.practice.service import PracticeService


class EdBasicaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=carregar_validado();cls.refs=[];cls.prova=[]
        for p in cls.corpus['paginas']:
            m=p['metadata'];aid=[s for s,_ in MATERIAIS].index(m['assunto'])+1
            cls.refs.append(dict(disciplina_slug='estrutura_de_dados',referencia_teorica=True,
                assunto_id=aid,assunto_principal_proposto=m['assunto'],conteudo=p['conteudo'],
                fontes=[dict(material_id=aid,titulo_material=m['titulo_material'],arquivo=m['arquivo'],pagina=m['pagina'],numero_questao=None)]))
        for c in cls.corpus['chunks']:
            if c['metadata']['tipo_material']=='PROVA_ANTIGA':
                m=c['metadata'];q=json.loads(c['conteudo'])
                cls.prova.append(dict(q,disciplina_slug='estrutura_de_dados',assunto_id=1 if m['assunto']=='fundamentos_c' else 3,
                    fontes=[dict(material_id=10,titulo_material=m['titulo_material'],arquivo=m['arquivo'],pagina=m['pagina'],numero_questao=m['numero_questao'])]))

    def test_corpus_reproduzivel_separado_da_avancada(self):
        self.assertEqual(self.corpus,consolidar())
        self.assertEqual(len(self.corpus['arquivos']),10)
        self.assertEqual(len(self.prova),4)
        self.assertEqual({c['metadata']['periodo'] for c in self.corpus['chunks']},{'02'})
        self.assertEqual({c['metadata']['disciplina'] for c in self.corpus['chunks']},{'estrutura_de_dados'})

    def test_todos_assuntos_tipos_com_fontes_passos_e_pseudocodigo(self):
        for slug in BANCOS:
            for tipo in ['CONCEITUAL','ESTILO_PROFESSOR','LOGICA','TESTE_MESA','MISTO']:
                qs=gerar(slug,self.refs,3,[],tipo=tipo,nivel='DIRETO')
                self.assertEqual(len(qs),3,(slug,tipo))
                for q in qs:
                    self.assertTrue(verificar(q));self.assertGreaterEqual(len(q['calculos']),3)
                    self.assertTrue(all(f['material_id']==[s for s,_ in MATERIAIS].index(slug)+1 for f in q['fontes']))
                    if tipo in {'TESTE_MESA','LOGICA'}:
                        self.assertIn('Pseudocódigo de apoio',q['resolucao'])
                        self.assertIn('Teste de mesa resolvido',q['resolucao'])
                        self.assertNotIn('Teste de mesa resolvido',q['enunciado'])

    def test_rejeita_gabarito_passos_e_alternativas_adulterados(self):
        q=gerar('ponteiros',self.refs,1,[],tipo='TESTE_MESA',nivel='DIRETO')[0]
        for campo,valor in [('calculos',['Falso']),('resolucao','Falso'),('gabarito',next(k for k in q['alternativas'] if k!=q['gabarito']))]:
            adulterada=copy.deepcopy(q);adulterada[campo]=valor
            with self.assertRaises(ValueError):verificar(adulterada)

    def test_pilhas_e_filas_conferidas_independentemente(self):
        for slug,esperado in [('filas','5 → 7'),('pilhas','3 → 7'),('listas','7 → 3')]:
            q=construir(dict(motor='estrutura_de_dados',assunto=slug,familia='TESTE_MESA',dados=dict(a=3,b=5,n=7)),random.Random(1))
            self.assertEqual(q['alternativas'][q['gabarito']],esperado)

    def test_contador_e_acumulador_independentes(self):
        for n in range(3,16):
            q=construir(dict(motor='estrutura_de_dados',assunto='logica_e_controle',familia='TESTE_MESA',dados=dict(a=5,b=3,n=n)),random.Random(1))
            self.assertEqual(int(q['alternativas'][q['gabarito']]),5+sum(range(2,n+1,2)))

    def test_narrativa_ia_preserva_codigo_e_recusa_novas_condicoes(self):
        qs=gerar('ponteiros',self.refs,1,[],tipo='TESTE_MESA',nivel='DIRETO')
        codigo=qs[0]['enunciado'];original=copy.deepcopy(qs[0])
        provedor=Mock(return_value=json.dumps(dict(contextos=['Uma equipe revisa um programa de cadastro antes de usá-lo no laboratório.'])))
        contextualizar(qs,'DETALHADO',provedor)
        self.assertTrue(qs[0]['enunciado'].endswith(codigo));self.assertTrue(verificar(qs[0]))
        ruim=Mock(return_value=json.dumps(dict(contextos=['O ponteiro soma 20 e a resposta correta muda.'])))
        with self.assertRaises(ValueError):contextualizar([original],'COTIDIANO',ruim)
        self.assertEqual(ruim.call_count,2)

    def test_sessao_oculta_resolucao_e_corrige_originais(self):
        repo=Mock();repo.buscar_questoes.return_value=self.prova
        service=PracticeService(repository=repo)
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=22,assunto_id=None,
            material_ids=[10],origem='PROVA',modo='CADASTRADAS',quantidade=10,excluir_fingerprints=[])
        qs=service.montar_questoes(req)['questoes'];self.assertEqual(len(qs),4)
        for q in qs:
            self.assertFalse({'spec','gabarito','calculos','resolucao'}&q.keys())
            secreta=service.sessoes[req['sessao_id']]['questoes'][q['id']]
            resposta=service.corrigir(dict(sessao_id=req['sessao_id'],usuario_id=1,questao_id=q['id'],alternativa=secreta['gabarito'],material_ids=[10]))
            self.assertTrue(resposta['correto']);self.assertTrue(resposta['calculos'])

    def test_sessao_gerada_usa_filtros_sem_narrador_de_estatistica(self):
        repo=Mock();repo.buscar_questoes.return_value=self.refs
        narrador=Mock(side_effect=AssertionError('Narrador da outra disciplina'))
        service=PracticeService(repository=repo,narrador=narrador)
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=22,assunto_id=None,
            material_ids=list(range(1,10)),origem='MISTO',modo='GERADAS_IA',quantidade=10,
            excluir_fingerprints=[],tipo_questao='TESTE_MESA',nivel_contexto='DIRETO')
        qs=service.montar_questoes(req)['questoes'];self.assertEqual(len(qs),10)
        narrador.assert_not_called()
        for q in service.sessoes[req['sessao_id']]['questoes'].values():
            self.assertEqual(q['spec']['familia'],'TESTE_MESA')
        vistos=[q['fingerprint'] for q in qs]
        novos=gerar('ponteiros',self.refs,10,vistos,tipo='TESTE_MESA',nivel='DIRETO')
        self.assertFalse(set(vistos)&{q['fingerprint'] for q in novos})

    def test_rejeita_referencias_da_disciplina_avancada(self):
        refs=copy.deepcopy(self.refs)
        for r in refs:r['disciplina_slug']='estrutura_de_dados_avancada'
        self.assertEqual(gerar('ponteiros',refs,1,[],nivel='DIRETO'),[])

    def test_indexacao_rejeita_outro_periodo_e_outro_assunto(self):
        a=self.corpus['arquivos'][0]
        material=dict(id=1,disciplina_id=22,periodo_id=2,periodo_numero=2,
            disciplina_slug='estrutura_de_dados',tipo='SLIDE_AULA',ativo=True,
            disciplina_ativa=True,periodo_ativo=True,fonte_monitor_virtual=True,
            referencia_externa='local:'+a['pdf'],assunto_id=1,
            titulo=a['titulo'],autorizacao_professor=False,disponivel_para_pratica=False)
        assuntos={a['assunto']:dict(id=1,disciplina_id=22,ativo=True)}
        chunks=preparar_material(material,assuntos)
        self.assertTrue(all(c['metadata']['periodo']=='02' and c['metadata']['disciplina_id']==22 for c in chunks))
        material['periodo_numero']=3
        with self.assertRaises(ValueError):preparar_material(material,assuntos)
        material['periodo_numero']=2;material['assunto_id']=9
        with self.assertRaises(ValueError):preparar_material(material,assuntos)


if __name__=='__main__':unittest.main()
