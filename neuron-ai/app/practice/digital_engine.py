"""Geração com fonte teórica por página e cálculo lógico independente do LLM."""
import hashlib
import json
import random
import secrets
import unicodedata
from app.practice.digital_bank import BANCOS

NUMERICAS = {
    'sistemas_analogicos_e_digitais': ['porta'],
    'circuitos_logicos': ['porta'],
    'portas_logicas_e_circuitos_digitais': ['porta'],
    'algebra_booleana': ['absorcao'],
    'contadores': ['contador', 'bits'],
    'logica_sequencial': ['registrador'],
    'maquinas_de_estados_finitos': ['estados'],
    'memorias': ['capacidade'],
    'circuitos_logicos_sequenciais': ['estados'],
    'projetos_de_circuitos_sequenciais': ['estados'],
}


def normal(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto.casefold()) if not unicodedata.combining(c))


def elaborar(spec):
    slug, familia, dados = spec['assunto'], spec['familia'], spec['dados']
    formula = substituicao = None
    if familia == 'conceitual':
        modelo = next(q for q in BANCOS[slug] if q['id'] == dados['id'])
        return dict(enunciado=modelo['enunciado'], conceito=modelo['conceito'],
            formula=None, substituicao=None, calculos=modelo['passos'],
            resolucao=modelo['correta'], erros_comuns=[modelo['erro']],
            dica='Identifique o requisito, diferencie os conceitos e confira cada alternativa com a regra estudada.'), modelo['correta'], modelo['erradas'], modelo['ancoras']
    if familia == 'porta':
        a,b,op = dados['a'],dados['b'],dados['op']
        valor = {'AND': a & b, 'OR': a | b, 'XOR': a ^ b, 'NAND': 1-(a & b), 'NOR': 1-(a | b)}[op]
        enunciado=f'Na bancada de teste de um controlador, uma porta {op} recebe A={a} e B={b}. Qual é o valor lógico da saída?'
        certo=f'{valor}.'
        erradas=[f'{1-valor}.', 'A saída precisa ser dois.', 'A saída depende necessariamente de um estado anterior.', 'Não existe saída definida para essas entradas numa porta ideal.']
        regras={'AND':'um somente se ambas as entradas forem um', 'OR':'um se pelo menos uma entrada for um', 'XOR':'um somente se as entradas forem diferentes', 'NAND':'o complemento de AND', 'NOR':'o complemento de OR'}
        passos=[f'Identifique a operação: {op} produz {regras[op]}.',f'Substitua as entradas: A={a}, B={b}.',f'Avalie a regra: saída={valor}.']
        ancora=[op]; conceito=f'Porta {op}'; erro='Não some entradas como números inteiros: aplique a operação lógica indicada.'
    elif familia == 'absorcao':
        # Contextos diferentes não são tratados como novas questões matemáticas.
        enunciado='O controle de uma lâmpada foi escrito como S=A OR (A AND B). Qual expressão mais simples preserva a saída em todas as combinações?'
        certo='S = A.'; erradas=['S = B.', 'S = A AND B.', 'S = A OR B.', 'S = NOT A.']
        passos=['Coloque A em evidência: A OR (A AND B) = A AND (1 OR B).', 'Use 1 OR B = 1.', 'Obtenha A AND 1 = A; confira os quatro pares de entrada na tabela-verdade.']
        formula='A + A·B = A'; ancora=['booleana']; conceito='Absorção booleana'; erro='OR e AND são operações booleanas; não aplique a soma aritmética usual.'
    elif familia == 'contador':
        n,pulsos,inicio=dados['n'],dados['pulsos'],dados['inicio']; modulo=2**n; valor=(inicio+pulsos)%modulo
        enunciado=f'Um contador binário crescente de {n} bits começa no valor decimal {inicio}. Cada pulso válido incrementa uma unidade, e após {modulo-1} ele volta a zero. Após {pulsos} pulsos válidos, qual é o valor decimal armazenado?'
        certo=str(valor); erradas=[str(v) for v in range(modulo+5) if v!=valor][:4]
        formula='Qfinal = (Qinicial + pulsos) mod 2^n'; substituicao=f'({inicio} + {pulsos}) mod {modulo}'
        passos=[f'Com {n} bits há {modulo} estados: de zero a {modulo-1}.',f'Some os pulsos: {inicio}+{pulsos}={inicio+pulsos}.',f'Tome o resto da divisão por {modulo}: {valor}.']
        ancora=['contador']; conceito='Contagem e retorno a zero'; erro='O maior valor é 2^n−1; o número de estados é 2^n.'
    elif familia in {'bits','estados'}:
        estados=dados['estados']; n=(estados-1).bit_length()
        enunciado=f'Um projeto precisa representar {estados} estados distintos com codificação binária compacta, sem exigência de um bit por estado. Qual é o menor número de bits necessário?'
        certo=str(n); erradas=[str(v) for v in range(max(0,n-2),n+6) if v!=n][:4]
        formula='Escolha o menor n inteiro com 2^n ≥ quantidade de estados.'
        passos=[f'O projeto exige {estados} códigos diferentes.',f'{n-1} bits fornecem {2**(n-1)} códigos, quantidade insuficiente.',f'{n} bits fornecem {2**n} códigos, suficientes; logo o mínimo é {n}.']
        ancora=['estado'] if familia=='estados' else ['contador']; conceito='Codificação binária de estados'; erro='Use o teto do logaritmo e não confunda código binário compacto com codificação de um bit por estado.'
    elif familia == 'registrador':
        n=dados['n']; valor=2**n
        enunciado=f'Um registrador tem {n} flip-flops, cada um armazenando um bit. Todos os padrões binários são permitidos. Quantos padrões distintos podem ser armazenados?'
        certo=str(valor); erradas=[str(n),str(2*n),str(valor-1),str(valor+1)]
        formula='Quantidade de padrões = 2^n'
        passos=[f'Cada um dos {n} bits admite duas possibilidades.',f'Multiplique duas possibilidades por posição: 2^{n}.',f'O resultado é {valor} padrões, incluindo o padrão todo zero.']
        ancora=['registrador']; conceito='Capacidade de um registrador'; erro='n é o número de bits; 2^n é a quantidade de padrões, e 2^n−1 é o maior valor sem sinal.'
    elif familia == 'capacidade':
        enderecos,bits=dados['enderecos'],dados['bits']; total=enderecos*bits; valor=total//8
        enunciado=f'Uma memória tem {enderecos} endereços distintos, cada um com uma palavra de {bits} bits. Considerando oito bits por byte e sem contar circuitos auxiliares, qual é a capacidade total em bytes?'
        certo=str(valor); erradas=[str(total),str(enderecos),str(valor*2),str(valor+bits)]
        formula='Capacidade em bytes = endereços × bits por palavra / 8'
        substituicao=f'{enderecos} × {bits} / 8'
        passos=[f'Cada endereço guarda {bits} bits.',f'Total de bits: {enderecos}×{bits}={total}.',f'Converta bits em bytes: {total}/8={valor}.']
        ancora=['palavra']; conceito='Organização e capacidade de memória'; erro='Diferencie quantidade de endereços, tamanho da palavra, bits e bytes.'
    else:
        raise ValueError('Família de Sistemas Digitais desconhecida.')
    if len(set([certo,*erradas]))!=5:
        raise ValueError('Alternativas duplicadas.')
    return dict(enunciado=enunciado, conceito=conceito, formula=formula, substituicao=substituicao,
        calculos=passos, resolucao=f'Resposta: {certo} ' + passos[-1], erros_comuns=[erro],
        dica='Separe dados e requisito; aplique a regra, confira um caso simples e verifique a unidade.'), certo,erradas,ancora


def fingerprint(spec):
    return hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()


def construir(spec, rng):
    corpo,certo,erradas,_=elaborar(spec)
    alternativas=[certo,*erradas];rng.shuffle(alternativas)
    q=dict(corpo,spec=spec,alternativas=dict(zip('ABCDE',alternativas)),
        gabarito='ABCDE'[alternativas.index(certo)],fingerprint=fingerprint(spec))
    verificar(q)
    return q


def verificar(q):
    corpo,certo,_,_=elaborar(q['spec'])
    if (set(q['alternativas'])!=set('ABCDE') or len(set(q['alternativas'].values()))!=5
            or q['alternativas'].get(q['gabarito'])!=certo or q['fingerprint']!=fingerprint(q['spec'])
            or any(q.get(k)!=v for k,v in corpo.items())):
        raise ValueError('Questão de Sistemas Digitais diverge da resolução conferida.')
    return True


def specs(slug, rng):
    for q in BANCOS.get(slug, []):
        yield dict(motor='sistemas_digitais',assunto=slug,familia='conceitual',dados={'id':q['id']})
    familias=NUMERICAS.get(slug, [])
    for i in range(300 if familias else 0):
        familia=familias[i%len(familias)]
        if familia=='porta': dados=dict(a=rng.randrange(2),b=rng.randrange(2),op=rng.choice(['AND','OR','XOR','NAND','NOR']))
        elif familia=='absorcao': dados={}
        elif familia=='contador':
            n=rng.randint(2,6); dados=dict(n=n,inicio=rng.randrange(2**n),pulsos=rng.randint(1,40))
        elif familia in {'bits','estados'}: dados=dict(estados=rng.randint(3,32))
        elif familia=='registrador': dados=dict(n=rng.randint(3,12))
        else: dados=dict(enderecos=2**rng.randint(5,12),bits=rng.choice([16,32,64]))
        yield dict(motor='sistemas_digitais',assunto=slug,familia=familia,dados=dados)


def gerar(slug, referencias, quantidade, excluidos):
    if not referencias or any(r.get('disciplina_slug')!='sistemas_digitais' for r in referencias):
        return []
    rng=random.Random(secrets.randbits(128)); vistos=set(excluidos); questoes=[]
    # Conceitos primeiro, depois aplicações com dados variados; nunca duplica só por trocar letras.
    candidatos=list(specs(slug,rng)); conceituais=candidatos[:len(BANCOS.get(slug,[]))]
    rng.shuffle(conceituais); candidatos[:len(conceituais)]=conceituais
    for spec in candidatos:
        if len(questoes)>=quantidade: break
        fp=fingerprint(spec)
        if fp in vistos: continue
        _,_,_,ancoras=elaborar(spec)
        fontes=[r for r in referencias if r['assunto_principal_proposto']==slug
                and all(normal(a) in normal(r['conteudo']) for a in ancoras)]
        if not fontes: continue
        # Página com maior desenvolvimento do conceito, em vez de escolher uma página ao acaso.
        ref=max(fontes,key=lambda r:sum(normal(r['conteudo']).count(normal(a)) for a in ancoras))
        q=construir(spec,rng)
        q.update(origem='GERADA_IA',fontes=ref['fontes'],resolucao_gerada_por_ia=True,
            origem_gabarito='GERADO_IA_CONFERIDO_LOGICAMENTE',
            aviso='Questão de estudo criada por IA com base no material teórico; não é da lista nem da prova do professor.')
        questoes.append(q);vistos.add(fp)
    return questoes
