import copy
import random
import unittest
import uuid
from unittest.mock import Mock
import sympy as s
from app.practice.integral_engine import TOPICOS,construir,elaborar,gerar,verificar,X,Y,Z
from app.practice.service import PracticeService,PracticeError
from app.rag.integral_corpus import carregar_validado
from app.rag.integral_search import ordenar_evidencias
from scripts.preparar_calculo2 import ASSUNTOS,corpus

class IntegralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=carregar_validado();cls.refs=[]
        for p in cls.data['paginas']:
            m=p['metadata'];aid=[a[0] for a in ASSUNTOS].index(m['assunto'])+1
            cls.refs.append(dict(disciplina_slug='calculo_para_computacao_2',referencia_teorica=True,assunto_id=aid,
                assunto_principal_proposto=m['assunto'],conteudo=p['conteudo'],
                fontes=[dict(material_id=aid,titulo_material=m['titulo_material'],arquivo=m['arquivo'],pagina=m['pagina'],numero_questao=None)]))

    def test_integridade_e_proveniencia(self):
        self.assertEqual(self.data,corpus())
        self.assertEqual(len(self.data['arquivos']),4)
        self.assertFalse(self.data['prova']['oficial'])
        for c in self.data['chunks']:
            m=c['metadata'];self.assertEqual(m['periodo'],'03')
            self.assertFalse(m['prova_oficial'])
            self.assertEqual(m['complementar'],m['assunto']=='base_multivariavel')
            if m['unidade']==1:self.assertIn(m['assunto'],[a[0] for a in ASSUNTOS[:3]])

    def test_geracao_todos_tipos_e_recusa_de_adulteracao(self):
        for t,(slug,u,_,tipos) in TOPICOS.items():
            for tipo in tipos:
                qs=gerar(slug,self.refs,3,[],unidade=u,topico=t,tipo_funcao=tipo)
                self.assertEqual(len(qs),3,(t,tipo));self.assertEqual(len({q['fingerprint'] for q in qs}),3)
                for q in qs:
                    self.assertTrue(verificar(q));self.assertIn('Tabela de Integrais',q['dica'])
                    bad=copy.deepcopy(q);bad['calculos'][0]='Etapa incorreta'
                    with self.assertRaises(ValueError):verificar(bad)
                    bad=copy.deepcopy(q);bad['alternativas']['A']='adulterado'
                    with self.assertRaises(ValueError):verificar(bad)

    def test_primitivas_e_distratores_nao_diferem_so_por_constante(self):
        q=construir(dict(motor='integral',topico='integral_direta',tipo_funcao='POLINOMIAL',parametros=[2,3,2,4]),random.Random(1))
        corpo,valor,f,_=elaborar(q['spec'])
        self.assertEqual(s.expand(s.diff(valor,X)-f),0)
        corretas=0
        for resposta in q['alternativas'].values():
            prim=s.sympify(resposta.replace(' + C','').replace('^','**'),locals={'x':X})
            corretas+=s.simplify(s.diff(prim,X)-f)==0
        self.assertEqual(corretas,1)

    def test_resultados_independentes(self):
        for t,esperado in [('integral_definida',s.Rational(20,3)),('dupla_retangulo',5),('dupla_iterada',6),('tripla_caixa',4),('tripla_iterada',s.Rational(7,8))]:
            spec=dict(motor='integral',topico=t,tipo_funcao='POLINOMIAL',parametros=[1,1,2,1])
            self.assertEqual(elaborar(spec)[1],esperado,t)

    def test_filtros_e_fontes_isolados(self):
        self.assertEqual(gerar('integrais_duplas_iteradas',self.refs,2,[],unidade=1),[])
        self.assertEqual(gerar('primitivas',self.refs,2,[],unidade=2),[])
        self.assertEqual(gerar('primitivas',[dict(self.refs[0],disciplina_slug='calculo_para_computacao_1')],2,[]),[])
        self.assertEqual(gerar('integrais_indefinidas',self.refs,2,[],tipo_funcao='IMPLICITA'),[])

    def test_simulados_e_segredo_ate_resposta(self):
        for unidade,ids in [(1,[1,2,3]),(2,[4,5,6,7]),(0,list(range(1,8)))]:
            repo=Mock();repo.buscar_questoes.return_value=self.refs;narrador=Mock(side_effect=AssertionError('Não deve narrar integrais'))
            svc=PracticeService(repository=repo,narrador=narrador)
            req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=30,assunto_id=None,assunto_ids=ids,
                     material_ids=list(range(1,9)),origem='MISTO',modo='GERADAS_IA',quantidade=10,unidade_calculo=unidade)
            publicas=svc.montar_questoes(req)['questoes'];self.assertEqual(len(publicas),10)
            self.assertFalse(any('gabarito' in q or 'resolucao' in q or 'calculos' in q for q in publicas))
            qs=svc.sessoes[req['sessao_id']]['questoes'].values()
            self.assertEqual({TOPICOS[q['spec']['topico']][0] for q in qs},{ASSUNTOS[i-1][0] for i in ids})
            narrador.assert_not_called()

    def test_busca_nao_inclui_complemento_sem_pedido(self):
        candidatos=[dict(metadata=p['metadata'],conteudo=p['conteudo']) for p in self.data['paginas']]
        rs=ordenar_evidencias(candidatos,'Explique integrais da primeira unidade',50)
        self.assertTrue(rs);self.assertTrue(all(r['metadata']['unidade']==1 for r in rs))
        rs=ordenar_evidencias(candidatos,'Como calcular integral tripla?',50)
        self.assertTrue(rs);self.assertTrue(all(r['metadata']['assunto'].startswith('integrais_triplas') for r in rs))
        linhas=[dict(assunto='integrais_duplas_retangulares',metadata=dict(unidade=2,complementar=False))]
        self.assertEqual(ordenar_evidencias(linhas,'Integrais duplas em retângulos',5),linhas)

    def test_pratica_padrao_nao_sorteia_complemento(self):
        repo=Mock();repo.buscar_questoes.return_value=self.refs;svc=PracticeService(repository=repo)
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=30,assunto_id=None,material_ids=list(range(1,9)),origem='MISTO',modo='GERADAS_IA',quantidade=10)
        svc.montar_questoes(req)
        self.assertTrue(all(q['spec']['topico']!='valor_multivariavel' for q in svc.sessoes[req['sessao_id']]['questoes'].values()))

if __name__=='__main__':unittest.main()
