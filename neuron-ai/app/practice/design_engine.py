"""Questões contextualizadas inspiradas no formato de situações-problema do ENEM."""
from app.practice.design_bank import BANCOS
from app.practice import curated_engine as base


def elaborar(spec):
    modelo = next(m for m in BANCOS[spec['assunto']] if m[0] == spec['id'])
    _, texto, certa, erradas, explicacao, erro, ancoras = modelo
    passos = ['Identifique a necessidade e as restrições descritas no texto-base.',
              explicacao, 'Compare as propostas com o objetivo solicitado, sem acrescentar condições ao cenário.']
    return dict(enunciado=texto, conceito=spec['assunto'].replace('_', ' ').capitalize(),
                formula=None, substituicao=None, calculos=passos, resolucao=explicacao,
                erros_comuns=[erro], dica='Use as evidências do cenário para justificar a decisão de design.'), certa, erradas, ancoras


def verificar(q):
    return base.verificar(q, elaborar)


def gerar(slug, referencias, quantidade, excluidos):
    def specs(rng):
        modelos = list(BANCOS.get(slug, []))
        rng.shuffle(modelos)
        return [dict(motor='design_de_artefatos_digitais', assunto=slug, id=m[0]) for m in modelos]
    return base.gerar_com_fontes(slug, referencias, quantidade, excluidos, specs, elaborar, 'design_de_artefatos_digitais')
