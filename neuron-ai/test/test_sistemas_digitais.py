import copy
import random
import unittest
import uuid
from unittest.mock import Mock
from app.rag.sistemas_digitais_corpus import carregar_validado, MATERIAIS
from app.practice.digital_bank import BANCOS
from app.practice.digital_engine import gerar, construir, verificar
from app.practice.service import PracticeService, PracticeError


class SistemasDigitaisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=carregar_validado()
        cls.refs=[]
        for p in cls.corpus['paginas']:
            m=p['metadata']; aid=[s for s,_ in MATERIAIS].index(m['assunto'])+1
            cls.refs.append(dict(disciplina_slug='sistemas_digitais',referencia_teorica=True,
                assunto_id=aid,assunto_principal_proposto=m['assunto'],conteudo=p['conteudo'],
                fontes=[dict(material_id=aid,titulo_material=m['titulo_material'],arquivo=m['arquivo'],
                             pagina=m['pagina'],numero_questao=None)]))

    def test_corpus_unico_com_paginas_e_fontes(self):
        self.assertEqual(len(self.corpus['arquivos']),12)
        self.assertEqual(len({a['pdf_sha256'] for a in self.corpus['arquivos']}),12)
        self.assertEqual(self.corpus['total_paginas'],189)
        self.assertEqual({c['metadata']['assunto'] for c in self.corpus['chunks']},set(BANCOS))

    def test_todos_conceitos_tem_fonte_e_resolucao(self):
        for slug,modelos in BANCOS.items():
            qs=gerar(slug,self.refs,100,[])
            conceituais={q['spec']['dados'].get('id') for q in qs}
            self.assertTrue({m['id'] for m in modelos}.issubset(conceituais),slug)
            for q in qs:
                self.assertTrue(verificar(q));self.assertGreaterEqual(len(q['calculos']),3)
                aid=[s for s,_ in MATERIAIS].index(slug)+1
                self.assertTrue(all(f['material_id']==aid for f in q['fontes']))
            repetidas=gerar(slug,self.refs,10,[q['fingerprint'] for q in qs])
            self.assertFalse({q['fingerprint'] for q in qs}&{q['fingerprint'] for q in repetidas})

    def test_portas_conferidas_por_tabelas_independentes(self):
        tabelas={'AND':[0,0,0,1],'OR':[0,1,1,1],'XOR':[0,1,1,0], 'NAND':[1,1,1,0],'NOR':[1,0,0,0]}
        for op,saida in tabelas.items():
            for i,(a,b) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
                q=construir(dict(motor='sistemas_digitais',assunto='portas_logicas_e_circuitos_digitais',
                    familia='porta',dados=dict(a=a,b=b,op=op)),random.Random(1))
                self.assertEqual(q['alternativas'][q['gabarito']],f'{saida[i]}.')

    def test_contador_simulado_pulso_a_pulso(self):
        for n in range(2,7):
            estado=2**n-2
            for pulsos in range(1,40):
                estado=0 if estado==2**n-1 else estado+1
                q=construir(dict(motor='sistemas_digitais',assunto='contadores',familia='contador',
                    dados=dict(n=n,inicio=2**n-2,pulsos=pulsos)),random.Random(1))
                self.assertEqual(int(q['alternativas'][q['gabarito']]),estado)

    def test_rejeita_gabarito_e_resolucao_adulterados(self):
        q=gerar('memoria_rom',self.refs,1,[])[0]
        for campo,valor in [('gabarito',next(k for k in q['alternativas'] if k!=q['gabarito'])),('calculos',['Incorreto'])]:
            adulterada=copy.deepcopy(q);adulterada[campo]=valor
            with self.assertRaises(ValueError): verificar(adulterada)

    def test_sessao_e_correcao_sem_expor_respostas(self):
        repo=Mock();repo.buscar_questoes.return_value=self.refs
        narrador=Mock(side_effect=AssertionError('Sistemas Digitais já contém contexto revisado.'))
        service=PracticeService(repository=repo,narrador=narrador)
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=50,assunto_id=None,
            material_ids=list(range(1,13)),origem='MISTO',modo='GERADAS_IA',quantidade=10,excluir_fingerprints=[])
        publicas=service.montar_questoes(req)['questoes']
        self.assertEqual(len(publicas),10)
        for q in publicas:
            self.assertFalse({'spec','gabarito','calculos','resolucao'}&q.keys())
            secreta=service.sessoes[req['sessao_id']]['questoes'][q['id']]
            resposta=dict(sessao_id=req['sessao_id'],usuario_id=1,questao_id=q['id'],
                alternativa=secreta['gabarito'],material_ids=req['material_ids'])
            correcao=service.corrigir(resposta)
            self.assertTrue(correcao['correto']);self.assertTrue(correcao['calculos'])
            self.assertEqual(service.corrigir(resposta),correcao)
        req.update(sessao_id=str(uuid.uuid4()),modo='CADASTRADAS')
        self.assertEqual(service.montar_questoes(req),{'questoes':[]})
        narrador.assert_not_called()


if __name__=='__main__': unittest.main()
