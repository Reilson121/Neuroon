import copy
import json
import unittest
import uuid
from pathlib import Path
from unittest.mock import Mock
from app.practice import ed_avancada_engine as ed, design_engine as design
from app.practice.design_bank import BANCOS
from app.practice.curated_engine import fingerprint
from app.practice.math_engine import verificar
from app.practice.service import PracticeService, PracticeError

ROOT = Path(__file__).resolve().parents[1]


def referencias(arquivo, disciplina):
    corpus = json.loads((ROOT/'saidas_testes'/arquivo).read_text(encoding='utf-8'))
    paginas = corpus.get('paginas',corpus['chunks'])
    slugs = sorted({p['metadata']['assunto'] for p in paginas})
    return [dict(disciplina_slug=disciplina,referencia_teorica=True,
        assunto_id=slugs.index(p['metadata']['assunto'])+1,
        assunto_principal_proposto=p['metadata']['assunto'],conteudo=p['conteudo'],
        fontes=[dict(material_id=1,titulo_material=p['metadata']['arquivo'],arquivo=p['metadata']['arquivo'],
                     pagina=p['metadata']['pagina'],numero_questao=None)]) for p in paginas]


class PraticaAvancadaDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edrefs=referencias('estrutura_de_dados_avancada_aula_0_aula_1_aula_2.json','estrutura_de_dados_avancada')
        cls.designrefs=referencias('design_de_artefatos_digitais_completa.json','design_de_artefatos_digitais')

    def test_cobertura_real_todos_assuntos_e_niveis(self):
        for slug in ed.CONCEITOS:
            for nivel in ['DIRETO','COTIDIANO','DETALHADO']:
                qs=ed.gerar(slug,self.edrefs,10,[],tipo='TESTE_MESA',nivel=nivel)
                self.assertEqual(len(qs),10,(slug,nivel))
                for q in qs:
                    self.assertTrue(verificar(q));self.assertTrue(q['fontes'])
                    self.assertIn('Teste de mesa resolvido',q['resolucao'])
                    self.assertNotIn('Teste de mesa resolvido',q['enunciado'])
                    if nivel=='DIRETO':self.assertTrue(q['enunciado'].startswith('```text'))
                    if nivel=='DETALHADO':self.assertIn('execução manual',q['enunciado'])
            self.assertEqual(len(ed.gerar(slug,self.edrefs,1,[],tipo='CONCEITUAL')),1)

    def test_banco_design_contextualizado_tem_27_itens_e_fontes(self):
        ids=set()
        for slug in BANCOS:
            qs=design.gerar(slug,self.designrefs,10,[])
            self.assertEqual(len(qs),3,slug)
            for q in qs:
                self.assertTrue(verificar(q));self.assertGreater(len(q['enunciado']),200)
                self.assertGreater(len(q['resolucao']),100)
                self.assertNotIn(q['fingerprint'],ids);ids.add(q['fingerprint'])
                self.assertTrue(q['fontes']);self.assertEqual(set(q['alternativas']),set('ABCDE'))
        self.assertEqual(len(ids),27)

    def test_casos_conhecidos_conferidos_independentemente(self):
        valores=[10,20,30]
        for slug,correta in [('filas_de_prioridade_e_heap','10 → 9'),('arvores_binarias_de_busca','20 → 30'),
                             ('arvores_balanceadas_e_avl','20'),('arvores_red_black','20'),('arvore_splay','10'),
                             ('grafos','10 → 20 → 30 → 31'),('algoritmos_de_ordenacao','10 → 20 → 9 → 30'),
                             ('arvores_em_python','30'),('conceitos_de_arvores','3')]:
            spec=dict(motor='estrutura_de_dados_avancada',assunto=slug,familia='TESTE_MESA',valores=valores,nivel='DIRETO')
            self.assertEqual(ed.elaborar(spec)[1],correta,slug)

    def test_gabarito_e_resolucao_nao_podem_ser_adulterados(self):
        for q in [design.gerar('matriz_csd',self.designrefs,1,[])[0],ed.gerar('grafos',self.edrefs,1,[],tipo='TESTE_MESA')[0]]:
            for k,v in [('resolucao','Uma conclusão diferente.'),('gabarito',next(k for k in q['alternativas'] if k!=q['gabarito']))]:
                outra=copy.deepcopy(q);outra[k]=v
                with self.assertRaises(ValueError):verificar(outra)
        spec=dict(motor='estrutura_de_dados_avancada',assunto='grafos',familia='TESTE_MESA',valores=[10,20,30],nivel='DIRETO')
        self.assertEqual(fingerprint(spec),fingerprint(dict(spec,nivel='DETALHADO')))

    def test_isolamento_disciplinas_e_exclusao(self):
        self.assertEqual(ed.gerar('grafos',self.designrefs,3,[]),[])
        self.assertEqual(design.gerar('matriz_csd',self.edrefs,3,[]),[])
        qs=design.gerar('matriz_csd',self.designrefs,3,[])
        self.assertEqual(design.gerar('matriz_csd',self.designrefs,3,[q['fingerprint'] for q in qs]),[])

    def sessao(self,refs,**kwargs):
        repo=Mock();repo.buscar_questoes.return_value=refs
        narrador=Mock(side_effect=AssertionError('Não deve usar o narrador de Estatística.'))
        service=PracticeService(repository=repo,narrador=narrador)
        req=dict(sessao_id=str(uuid.uuid4()),usuario_id=1,disciplina_id=47,assunto_id=None,material_ids=[1],
                 origem='MISTO',modo='GERADAS_IA',quantidade=10,excluir_fingerprints=[],**kwargs)
        return service,req

    def test_simulado_cobre_somente_os_conteudos_selecionados_e_oculta_gabaritos(self):
        escolhidos=[r['assunto_id'] for r in self.designrefs if r['assunto_principal_proposto'] in {'matriz_csd','design_thinking','publico_alvo'}]
        escolhidos=sorted(set(escolhidos))
        service,req=self.sessao(self.designrefs,assunto_ids=escolhidos)
        qs=service.montar_questoes(req)['questoes']
        self.assertEqual(len(qs),9)
        for q in qs:self.assertFalse({'gabarito','spec','resolucao','calculos'}&q.keys())
        segredos=service.sessoes[req['sessao_id']]['questoes']
        self.assertEqual({q['spec']['assunto'] for q in segredos.values()},{'matriz_csd','design_thinking','publico_alvo'})
        q=next(iter(segredos.values()))
        resposta=service.corrigir(dict(sessao_id=req['sessao_id'],usuario_id=1,questao_id=q['id'],alternativa=q['gabarito'],material_ids=[1]))
        self.assertTrue(resposta['correto']);self.assertTrue(resposta['resolucao'])

    def test_sessao_avancada_toda_disciplina_ignora_ementa(self):
        service,req=self.sessao(self.edrefs,tipo_questao='TESTE_MESA',nivel_contexto='DIRETO')
        qs=service.montar_questoes(req)['questoes'];self.assertEqual(len(qs),10)
        for q in qs:self.assertTrue(q['enunciado'].startswith('```text'))
        service.narrador.assert_not_called()

    def test_pratica_variada_inclui_conceitos_e_execucao_manual(self):
        service,req=self.sessao(self.edrefs,tipo_questao='MISTO',nivel_contexto='DETALHADO')
        service.montar_questoes(req)
        qs=service.sessoes[req['sessao_id']]['questoes'].values()
        self.assertEqual({q['spec']['familia'] for q in qs},{'CONCEITUAL','TESTE_MESA'})

    def test_rejeita_conteudo_inexistente_e_quantidade_menor_que_selecao(self):
        for ids in [[999],[1,2]]:
            service,req=self.sessao(self.designrefs,assunto_ids=ids)
            req['quantidade']=1
            with self.assertRaises(PracticeError):service.montar_questoes(req)


if __name__=='__main__':unittest.main()
