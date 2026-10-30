"""Montagem de exercícios autorais conferidos e fontes teóricas por assunto."""
import hashlib
import json
import random
import secrets
import unicodedata


def normal(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto.casefold()) if not unicodedata.combining(c))


def fingerprint(spec):
    # Contextualização e ordem das alternativas não tornam um exercício novo.
    base = {k: v for k, v in spec.items() if k != 'nivel'}
    return hashlib.sha256(json.dumps(base, sort_keys=True).encode()).hexdigest()


def construir(spec, elaborar, rng):
    corpo, certa, erradas, _ = elaborar(spec)
    opcoes = [certa, *erradas]
    if len(opcoes) != 5 or len(set(opcoes)) != 5:
        raise ValueError('O exercício exige cinco alternativas distintas.')
    rng.shuffle(opcoes)
    return dict(corpo, spec=spec, alternativas=dict(zip('ABCDE', opcoes)),
                gabarito='ABCDE'[opcoes.index(certa)], fingerprint=fingerprint(spec))


def verificar(q, elaborar):
    corpo, certa, erradas, _ = elaborar(q['spec'])
    if (set(q['alternativas']) != set('ABCDE') or
        set(q['alternativas'].values()) != set([certa, *erradas]) or
        q['alternativas'].get(q['gabarito']) != certa or
        q['fingerprint'] != fingerprint(q['spec']) or
        any(q.get(k) != v for k, v in corpo.items())):
        raise ValueError('Exercício diverge do enunciado e da resolução conferidos.')
    return True


def gerar_com_fontes(slug, referencias, quantidade, excluidos, specs, elaborar, disciplina):
    if not referencias or any(r.get('disciplina_slug') != disciplina for r in referencias):
        return []
    rng = random.Random(secrets.randbits(128))
    candidatos = list(specs(rng))
    vistos = set(excluidos)
    questoes = []
    for spec in candidatos:
        if len(questoes) >= quantidade:
            break
        ident = fingerprint(spec)
        if ident in vistos:
            continue
        _, _, _, ancoras = elaborar(spec)
        fontes = [r for r in referencias if r['assunto_principal_proposto'] == slug
                  and any(normal(a) in normal(r.get('conteudo', '')) for a in ancoras)]
        if not fontes:
            continue
        ref = max(fontes, key=lambda r: sum(normal(r['conteudo']).count(normal(a)) for a in ancoras))
        q = construir(spec, elaborar, rng)
        q.update(origem='GERADA_IA', fontes=ref['fontes'], resolucao_gerada_por_ia=True,
                 origem_gabarito='AUTORAL_IA_CONFERIDO',
                 aviso='Exercício autoral de estudo, com base nas aulas disponíveis. Não é questão oficial nem reprodução de prova.')
        questoes.append(q)
        vistos.add(ident)
    return questoes


def tabela(cabecalhos, linhas):
    return '\n'.join(['| ' + ' | '.join(cabecalhos) + ' |',
                      '| ' + ' | '.join(['---'] * len(cabecalhos)) + ' |',
                      *['| ' + ' | '.join(str(v) for v in linha) + ' |' for linha in linhas]])
