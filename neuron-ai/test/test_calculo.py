import copy
import json
import random
import unittest
import uuid
from unittest.mock import Mock,MagicMock
import sympy as s
from app.rag.calculo_corpus import carregar_validado,consolidar,preparar_material,ASSUNTOS
from app.practice.calculo_engine import TOPICOS,gerar,verificar,construir,elaborar,X
from app.practice.service import PracticeService,PracticeError
from app.practice.repository import QuestionRepository


class CalculoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=carregar_validado();cls.refs=[]
        for p in cls.corpus['paginas']:
            m=p['metadata'];aid=[a[0] for a in ASSUNTOS].index(m['assunto'])+1
            cls.refs.append(dict(disciplina_slug='calculo_para_computacao_1',referencia_teorica=True,
                assunto_id=aid,assunto_principal_proposto=m['assunto'],conteudo=p['conteudo'],
                fontes=[dict(material_id=aid,titulo_material=m['titulo_material'],arquivo=m['arquivo'],pagina=m['pagina'],numero_questao=None)]))

    def test_corpus_reproduzivel_integridade_unidades_e_ids(self):
        self.assertEqual(self.corpus,consolidar())
        self.assertEqual(len(self.corpus['arquivos']),5)
        self.assertEqual(self.corpus['total_paginas'],202)
        chunks=self.corpus['chunks']
        self.assertEqual(len({c['chunk_id'] for c in chunks}),len(chunks))
        self.assertFalse(self.corpus['prova']['unidade_2_disponivel'])
        for c in chunks:
            m=c['metadata'];self.assertEqual(m['periodo'],'02')
            self.assertEqual(m['chunk_id'],c['chunk_id'])
            self.assertEqual(m['unidade'],2 if m['assunto'] in {'derivada_definicao','regras_derivacao','derivacao_implicita','aplicacoes_derivada'} else 1)

    def test_todos_topicos_e_tipos_com_fontes_e_etapas(self):
        for topico,(slug,unidade,_,tipos) in TOPICOS.items():
            for tipo in tipos:
                qs=gerar(slug,self.refs,10,[],unidade=unidade,topico=topico,tipo_funcao=tipo)
                self.assertEqual(len(qs),10,(topico,tipo))
                self.assertEqual(len({q['fingerprint'] for q in qs}),10)
                for q in qs:
                    self.assertTrue(verificar(q));self.assertGreaterEqual(len(q['calculos']),4)
                    self.assertTrue(q['fontes']);self.assertTrue(q['enunciado'].startswith(('Calcule','Dadas','Simplifique','Considere','Para','Um quadrado','Use')))
                    self.assertEqual(q['spec']['tipo_funcao'],tipo)
                    if unidade==2:self.assertIn('Tabela de Derivadas',q['dica'])

    def test_filtragem_nao_faz_fallback_entre_unidades_ou_regras(self):
        self.assertEqual(gerar('limites',self.refs,2,[],unidade=2),[])
        self.assertEqual(gerar('regras_derivacao',self.refs,2,[],unidade=1),[])
        self.assertEqual(gerar('regras_derivacao',self.refs,2,[],topico='produto',tipo_funcao='RADICAL'),[])
        self.assertEqual(gerar('regras_derivacao',[dict(self.refs[0],disciplina_slug='estatistica')],2,[]),[])

    def test_resultados_independentes_com_derivacao_numerica(self):
        from app.practice.calculo_engine import elaborar
        # Regra da cadeia trigonométrica e produto: diferenças centrais, sem usar diff.
        for topico,tipo,f in [('cadeia','TRIGONOMETRICA',lambda x:s.sin(3*x+2)),
                              ('produto','POLINOMIAL',lambda x:(3*x+2)*(x**4+5))]:
            spec=dict(motor='calculo',topico=topico,tipo_funcao=tipo,parametros=[3,2,4,5])
            _,derivada=elaborar(spec);h=1e-5;p=0.7
            aprox=float((f(p+h)-f(p-h))/(2*h))
            self.assertAlmostEqual(float(derivada.subs(X,p)),aprox,places=5)
        for topico,esperado in [('fatoracao_limite','54'),('racionalizacao','1/6'),('infinito','3/5'),('relacionadas','12')]:
            tipo=TOPICOS[topico][3][0];q=construir(dict(motor='calculo',topico=topico,tipo_funcao=tipo,parametros=[3,2,4,5]),random.Random(1))
            self.assertEqual(q['alternativas'][q['gabarito']],esperado)

    def test_rejeita_passos_gabarito_e_enunciado_adulterados(self):
        q=gerar('regras_derivacao',self.refs,1,[],topico='cadeia')[0]
        for campo,valor in [('calculos',['Falso']),('enunciado','Calcule outro valor.'),('gabarito',next(k for k in q['alternativas'] if k!=q['gabarito']))]:
            ruim=copy.deepcopy(q);ruim[campo]=valor
            with self.assertRaises(ValueError):verificar(ruim)

    def test_sessao_filtra_esconde_solucao_e_corrige(self):
        repo=Mock();repo.buscar_questoes.return_value=self.refs;narrador=Mock(side_effect=AssertionError('Não usar narrador de Estatística.'))
        service=PracticeService(repository=repo,narrador=narrador)
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=23,assunto_id=None,
            material_ids=list(range(1,10)),origem='MISTO',modo='GERADAS_IA',quantidade=3,
            unidade_calculo=2,topico_calculo='cadeia',tipo_funcao='RADICAL')
        qs=service.montar_questoes(req)['questoes'];self.assertEqual(len(qs),3);narrador.assert_not_called()
        for q in qs:
            self.assertFalse({'spec','gabarito','calculos','resolucao'}&q.keys())
            segredo=service.sessoes[req['sessao_id']]['questoes'][q['id']]
            self.assertEqual(segredo['spec']['topico'],'cadeia');self.assertEqual(segredo['spec']['tipo_funcao'],'RADICAL')
            resposta=service.corrigir(dict(sessao_id=req['sessao_id'],usuario_id=1,questao_id=q['id'],alternativa=segredo['gabarito'],material_ids=list(range(1,10))))
            self.assertTrue(resposta['correto']);self.assertTrue(resposta['calculos'])
        novos=gerar('regras_derivacao',self.refs,3,[q['fingerprint'] for q in qs],topico='cadeia',tipo_funcao='RADICAL')
        self.assertFalse({q['enunciado'] for q in qs}&{q['enunciado'] for q in novos})

    def test_material_de_outro_periodo_e_arquivo_falso_recusados(self):
        with self.assertRaises(ValueError):preparar_material(dict(disciplina_slug='calculo_para_computacao_1',periodo_numero=3),{})

    def test_opcoes_interface_correspondem_ao_motor(self):
        from app.rag.calculo_corpus import RAIZ
        dados=json.loads((RAIZ.parent/'frontend/src/calculo-topicos.json').read_text(encoding='utf-8'))
        self.assertEqual({d['id'] for d in dados},set(TOPICOS))
        for d in dados:self.assertEqual((d['assunto'],d['unidade'],d['nome'],d['tipos']),TOPICOS[d['id']])

    def test_pagina_compartilhada_preserva_todos_os_assuntos(self):
        linhas=[dict(conteudo=ref['conteudo'],metadata={},pagina=f['pagina'],arquivo=f['arquivo'],
                     assunto=ref['assunto_principal_proposto'],material_id=100,titulo=f['titulo_material'],
                     assunto_id=ref['assunto_id'],disciplina_slug='calculo_para_computacao_1')
                for ref in self.refs for f in ref['fontes'] if f['arquivo'].startswith('prova')]
        store=MagicMock();cur=store._conectar.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchall.return_value=linhas
        refs=QuestionRepository(store).buscar_teoria(23,None,[100])
        self.assertEqual({r['assunto_principal_proposto'] for r in refs},{a[0] for a in ASSUNTOS[:5]})
        self.assertEqual(len(gerar('simplificacao_algebrica',refs,10,[],topico='fatoracao')),10)

    def test_fatoracao_nao_esgota_com_historico_maximo(self):
        vistos=set()
        for _ in range(21):
            qs=gerar('simplificacao_algebrica',self.refs,10,vistos,topico='fatoracao')
            self.assertEqual(len(qs),10)
            novos={q['fingerprint'] for q in qs}
            self.assertFalse(vistos & novos);vistos.update(novos)

    def test_familias_de_fatoracao_e_inversa_conferidas_independentemente(self):
        for n,resto in [(2,2*(X+3)),(3,2*X+5),(4,2*(X**2+3*X+9)),(5,2*(X-3))]:
            spec=dict(motor='calculo',topico='fatoracao',tipo_funcao='RACIONAL',parametros=[3,2,n,5])
            corpo,resultado=elaborar(spec)
            self.assertEqual(s.simplify(resultado-resto),0)
            self.assertIn('x ≠ 3',corpo['calculos'][-1])
            spec['topico']='fatoracao_limite'
            self.assertEqual(elaborar(spec)[1],s.limit(s.expand((X-3)*resto)/(X-3),X,3))
        spec=dict(topico='inversa',tipo_funcao='EXPONENCIAL',parametros=[3,2,4,5])
        inversa=elaborar(spec)[1]
        self.assertEqual(s.simplify(3*s.exp(inversa)+2),X)

    def test_simulados_cobrem_selecao_unidades_final_e_segunda_chamada(self):
        for ids in [[1,3],[1,2,3,4,5],[6,7,8,9],list(range(1,10)),list(range(1,10))]:
            repo=Mock();repo.buscar_questoes.return_value=self.refs
            service=PracticeService(repository=repo)
            req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=23,assunto_id=None,
                     assunto_ids=ids,material_ids=list(range(1,10)),origem='MISTO',modo='GERADAS_IA',quantidade=10)
            qs=service.montar_questoes(req)['questoes']
            self.assertEqual(len(qs),10)
            segredos=service.sessoes[req['sessao_id']]['questoes'].values()
            cobertos={TOPICOS[q['spec']['topico']][0] for q in segredos}
            self.assertEqual(cobertos,{ASSUNTOS[i-1][0] for i in ids})
            self.assertFalse(any('gabarito' in q or 'resolucao' in q for q in qs))

    def test_prova_nao_omite_assunto_sem_fonte_ou_com_filtro_incompativel(self):
        repo=Mock();repo.buscar_questoes.return_value=self.refs
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=23,assunto_id=None,
                 assunto_ids=[1,6],material_ids=list(range(1,10)),origem='MISTO',modo='GERADAS_IA',quantidade=10,unidade_calculo=1)
        with self.assertRaises(PracticeError):PracticeService(repository=repo).montar_questoes(req)


if __name__=='__main__':unittest.main()
