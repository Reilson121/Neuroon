"""Exercícios diretos parametrizados, com gabarito simbólico e etapas verificáveis.

Não chama o narrador de Estatística: os comandos de Cálculo devem permanecer
curtos. Os exercícios inéditos são identificados, sem alegar autoria docente.
"""
import copy
import hashlib
import json
import random
import secrets
from functools import lru_cache
import sympy as s

X = s.Symbol('x', real=True)
# tópico: assunto, unidade, rótulo, tipos de função compatíveis
TOPICOS = {
 'composicao': ('funcoes_compostas',1,'Composição de funções',['POLINOMIAL','RACIONAL','RADICAL']),
 'composicao_valor': ('funcoes_compostas',1,'Valor numérico da composição',['POLINOMIAL']),
 'inversa': ('funcoes_inversas',1,'Cálculo da inversa',['AFIM','EXPONENCIAL']),
 'soma_inversas': ('funcoes_inversas',1,'Soma de funções inversas',['AFIM']),
 'fatoracao': ('simplificacao_algebrica',1,'Fatoração e simplificação',['RACIONAL']),
 'substituicao': ('limites',1,'Limites por substituição',['POLINOMIAL','RACIONAL','RADICAL']),
 'fatoracao_limite': ('limites',1,'Indeterminação 0/0 por fatoração',['RACIONAL']),
 'racionalizacao': ('limites',1,'Indeterminação 0/0 por racionalização',['RADICAL']),
 'infinito': ('limites',1,'Limites no infinito',['RACIONAL']),
 'infinito_ponto': ('limites',1,'Limite infinito em um ponto',['RACIONAL']),
 'confronto': ('limites',1,'Teorema do confronto',['TRIGONOMETRICA']),
 'laterais': ('continuidade',1,'Limites laterais e continuidade',['POR_PARTES']),
 'definicao': ('derivada_definicao',2,'Derivada pela definição',['POLINOMIAL']),
 'potencia': ('regras_derivacao',2,'Constante, potência, soma e subtração',['POLINOMIAL','RADICAL','RACIONAL']),
 'produto': ('regras_derivacao',2,'Regra do produto',['POLINOMIAL','TRIGONOMETRICA','EXPONENCIAL']),
 'quociente': ('regras_derivacao',2,'Regra do quociente',['RACIONAL','TRIGONOMETRICA','LOGARITMICA']),
 'cadeia': ('regras_derivacao',2,'Regra da cadeia',['POLINOMIAL','RADICAL','TRIGONOMETRICA','EXPONENCIAL','LOGARITMICA']),
 'trigonometrica': ('regras_derivacao',2,'Derivadas trigonométricas',['TRIGONOMETRICA']),
 'exponencial': ('regras_derivacao',2,'Derivadas exponenciais',['EXPONENCIAL']),
 'logaritmica': ('regras_derivacao',2,'Derivadas logarítmicas',['LOGARITMICA']),
 'hiperbolica': ('regras_derivacao',2,'Derivadas hiperbólicas',['HIPERBOLICA']),
 'implicita': ('derivacao_implicita',2,'Derivação implícita',['IMPLICITA']),
 'tangente': ('aplicacoes_derivada',2,'Reta tangente',['POLINOMIAL']),
 'taxa': ('aplicacoes_derivada',2,'Taxa de variação instantânea',['POLINOMIAL']),
 'crescimento': ('aplicacoes_derivada',2,'Crescimento e decaimento exponencial',['EXPONENCIAL']),
 'relacionadas': ('aplicacoes_derivada',2,'Taxas relacionadas',['POLINOMIAL']),
 'linearizacao': ('aplicacoes_derivada',2,'Aproximação linear',['RADICAL']),
 'diferencial': ('aplicacoes_derivada',2,'Diferenciais',['POLINOMIAL']),
}


def texto(expr):
    return s.sstr(expr).replace('**','^').replace('sin(', 'sen(').replace('log(', 'ln(')


def fingerprint(spec):
    # Parâmetros não usados não podem fazer uma questão repetida parecer inédita.
    corpo,_=elaborar(spec)
    return hashlib.sha256(corpo['enunciado'].encode()).hexdigest()


def fonte_compativel(topico,ref):
    """A referência aponta para a seção correspondente, não uma página aleatória."""
    intervalos={
        'composicao':('01 ',1,9),'composicao_valor':('01 ',1,9),'inversa':('01 ',21,28),'soma_inversas':('01 ',21,28),
        'substituicao':('02 ',17,21),'fatoracao_limite':('02 ',20,24),
        'racionalizacao':('02 ',20,24),'infinito':('02 ',45,54),'infinito_ponto':('02 ',10,13),
        'confronto':('02 ',22,25),'laterais':('02 ',35,42),'definicao':('02 ',57,72),
        'potencia':('03 ',2,6),'produto':('03 ',11,14),'quociente':('03 ',11,14),
        'cadeia':('03 ',23,28),'trigonometrica':('03 ',17,21),'exponencial':('03 ',6,8),
        'logaritmica':('03 ',40,44),'hiperbolica':('03 ',76,79),'implicita':('03 ',32,37),
        'tangente':('02 ',57,62),'taxa':('03 ',45,53),'crescimento':('03 ',57,61),
        'relacionadas':('03 ',64,67),'linearizacao':('03 ',70,73),'diferencial':('03 ',72,73)}
    for f in ref['fontes']:
        nome=f.get('arquivo','');pagina=f.get('pagina',0)
        if nome.startswith('prova'):
            if topico in {'composicao','composicao_valor','inversa','soma_inversas','fatoracao','substituicao'} and pagina==1 or topico in {'fatoracao_limite','laterais'} and pagina==2:return True
        if topico in intervalos:
            prefixo,inicio,fim=intervalos[topico]
            if nome.startswith(prefixo) and inicio<=pagina<=fim:return True
        if nome.startswith('Tabela') and topico in {'potencia','produto','quociente','cadeia','trigonometrica','exponencial','logaritmica'} and pagina==1:return True
    return False


def elaborar(spec):
    corpo,valor=_elaborar_cached(spec['topico'],spec['tipo_funcao'],tuple(spec['parametros']))
    return copy.deepcopy(corpo),valor


@lru_cache(maxsize=1024)
def _elaborar_cached(topico,tipo_funcao,parametros):
    spec=dict(topico=topico,tipo_funcao=tipo_funcao,parametros=parametros)
    t=spec['topico']; tipo=spec['tipo_funcao']; a,b,n,c=map(s.Integer,spec['parametros'])
    if t not in TOPICOS or tipo not in TOPICOS[t][3] or not(1<=a<=9 and 1<=b<=9 and 2<=n<=5 and 1<=c<=9):
        raise ValueError('Parâmetros de Cálculo inválidos.')
    x=X; passos=[]; formula=''; erros=['Respeite o domínio original e os parênteses.']
    dominio=''; resposta=None
    if t in {'composicao','composicao_valor'}:
        f=a*x+b
        g=x**2-c if tipo=='POLINOMIAL' else 1/(x+c) if tipo=='RACIONAL' else s.sqrt(x+c)
        resposta=s.simplify(f.subs(x,g));pergunta=f'Dadas f(x) = {texto(f)} e g(x) = {texto(g)}, calcule (f∘g)(x).'
        formula='(f∘g)(x) = f(g(x))'
        passos=[f'Identifique a função externa f(x) = {texto(f)} e a interna g(x) = {texto(g)}.',
            f'Substitua cada x de f por g(x): f(g(x)) = {a}*({texto(g)}) + {b}.',f'Efetue as operações: {texto(resposta)}.']
        dominio=f'x ≠ {-c}' if tipo=='RACIONAL' else f'x ≥ {-c}' if tipo=='RADICAL' else 'x real'
        erros=['A ordem importa: f(g(x)) em geral é diferente de g(f(x)).']
        if t=='composicao_valor':
            resposta=f.subs(x,g.subs(x,c))
            pergunta=f'Dadas f(x) = {texto(f)} e g(x) = {texto(g)}, calcule f(g({c})).'
            passos=[f'Calcule primeiro a interna: g({c}) = {g.subs(x,c)}.',
                f'Substitua esse resultado em f: f({g.subs(x,c)}) = {a}*({g.subs(x,c)}) + {b}.',f'Efetue as operações: {texto(resposta)}.']
    elif t=='inversa':
        f=a*x+b if tipo=='AFIM' else s.exp(x)+b
        resposta=(x-b)/a if tipo=='AFIM' else s.log(x-b)
        pergunta=f'Calcule a função inversa de f(x) = {texto(f)}.';formula='Trocar x e y e isolar y.'
        passos=[f'Escreva y = {texto(f)}.',f'Troque x e y: x = {texto(f.subs(x,s.Symbol("y")))}.',
            f'Isole y: y = {texto(resposta)}.',f'Portanto, f⁻¹(x) = {texto(resposta)}.']
        dominio='x real' if tipo=='AFIM' else f'x > {b}'
        erros=['f⁻¹(x) não significa 1/f(x).']
    elif t=='soma_inversas':
        f=a*x;g=b*x+c;resposta=x/a+(x-c)/b
        pergunta=f'Dadas f(x) = {texto(f)} e g(x) = {texto(g)}, calcule f⁻¹(x) + g⁻¹(x).';formula='Trocar x e y, isolar y e somar as inversas.'
        passos=[f'Para f: x = {a}*y, então f⁻¹(x) = x/{a}.',
            f'Para g: x = {b}*y + {c}, então g⁻¹(x) = (x − {c})/{b}.',
            f'Some: x/{a} + (x − {c})/{b} = {texto(s.simplify(resposta))}.'];dominio='x real'
    elif t in {'fatoracao','fatoracao_limite'}:
        numer=x*x-a*a;den=x-a; f=numer/den; resposta=x+a if t=='fatoracao' else 2*a
        pergunta=f'Simplifique ({texto(numer)})/({texto(den)}), indicando a restrição do domínio.' if t=='fatoracao' else f'Calcule lim(x → {a}) ({texto(numer)})/({texto(den)}).'
        formula='x² − a² = (x − a)(x + a)'
        passos=([f'A substituição x = {a} produz 0/0; isso é uma indeterminação, não o resultado.'] if t!='fatoracao' else [])+[
            f'Fatore o numerador: {texto(numer)} = ({texto(x-a)})*({texto(x+a)}).',
            f'Para x ≠ {a}, cancele o fator ({texto(x-a)}): resta {texto(x+a)}.']
        if t=='fatoracao_limite': passos.append(f'Agora substitua x = {a}: {a} + {a} = {2*a}.')
        else: dominio=f'x ≠ {a}'
        erros=['Nunca cancele parcelas de uma soma; cancele somente fatores.','0/0 não é zero.']
    elif t=='substituicao':
        f=a*x*x+b*x+c if tipo=='POLINOMIAL' else (a*x+b)/(x*x+c) if tipo=='RACIONAL' else s.sqrt(x+b)
        resposta=f.subs(x,c); pergunta=f'Calcule lim(x → {c}) {texto(f)}.';formula='Substituição direta em função contínua no ponto.'
        passos=[f'Verifique o domínio em x = {c}: a expressão está definida.',
            f'A função é contínua nesse ponto; substitua x por {c}.',f'Calcule: {texto(resposta)}.']
    elif t=='racionalizacao':
        f=(s.sqrt(x)-a)/(x-a*a);resposta=1/(2*a)
        pergunta=f'Calcule lim(x → {a*a}) (sqrt(x) − {a})/(x − {a*a}).';formula='(√x − a)(√x + a) = x − a²'
        passos=[f'A substituição x = {a*a} dá 0/0.',f'Multiplique numerador e denominador pelo conjugado sqrt(x) + {a}.',
            f'Cancele x − {a*a} para x ≠ {a*a}: fica 1/(sqrt(x) + {a}).',f'Substitua: 1/({a} + {a}) = {texto(resposta)}.']
    elif t=='infinito':
        f=(a*x*x+b)/(c*x*x+1);resposta=a/c
        pergunta=f'Calcule lim(x → +∞) ({texto(a*x*x+b)})/({texto(c*x*x+1)}).';formula='Dividir numerador e denominador pela maior potência de x.'
        passos=[f'Divida por x²: ({a} + {b}/x²)/({c} + 1/x²).','Quando x → +∞, 1/x² → 0.',f'O limite é {a}/{c} = {texto(resposta)}.']
    elif t=='infinito_ponto':
        resposta='+∞';pergunta=f'Calcule lim(x → {a}) {b}/(x − {a})².';formula='Uma constante positiva dividida por quantidade positiva que tende a zero cresce sem limite.'
        passos=[f'Quando x → {a}, (x − {a})² → 0.',f'Para x ≠ {a}, o denominador é positivo, tanto pela esquerda quanto pela direita.',
            f'Como {b} > 0, ambos os limites laterais são +∞.']
    elif t=='confronto':
        resposta=s.Integer(0);pergunta=f'Calcule lim(x → 0) {a}*x²*sen({b}/x).';formula='−1 ≤ sen(u) ≤ 1; teorema do confronto.'
        passos=[f'Para x ≠ 0, −{a}*x² ≤ {a}*x²*sen({b}/x) ≤ {a}*x².',
            'Os dois extremos tendem a 0 quando x → 0.','Pelo teorema do confronto, o limite é 0.']
    elif t=='laterais':
        resposta='Sim, é contínua.' if n%2==0 else 'Não, os limites laterais são diferentes.'
        direita=a+b if n%2==0 else a+b+c
        pergunta=f'Considere f(x) = {a}*x + {b} se x < 1, f(1) = {a+b} e f(x) = {a}*x + {direita-a} se x > 1. Calcule os limites laterais em 1 e verifique a continuidade.'
        formula='Continuidade: lim(x→p⁻) f(x) = lim(x→p⁺) f(x) = f(p).'
        passos=[f'Pela esquerda: {a}*1 + {b} = {a+b}.',f'Pela direita: {a}*1 + {direita-a} = {direita}.',
            f'Valor no ponto: f(1) = {a+b}.',resposta]
    elif t=='definicao':
        f=a*x*x+b*x+c;resposta=2*a*x+b;h=s.Symbol('h')
        pergunta=f'Calcule f′(x) pela definição, para f(x) = {texto(f)}.';formula='f′(x) = lim(h→0) [f(x+h) − f(x)]/h'
        diff=s.expand(f.subs(x,x+h)-f)
        passos=[f'Calcule f(x+h) = {texto(s.expand(f.subs(x,x+h)))}.',f'Subtraia f(x): {texto(diff)}.',
            f'Divida por h ≠ 0: {texto(s.cancel(diff/h))}.',f'Tome h → 0: f′(x) = {texto(resposta)}.']
    elif t in {'potencia','produto','quociente','cadeia','trigonometrica','exponencial','logaritmica','hiperbolica'}:
        if t=='potencia':
            f=a*x**n+b*x+c if tipo=='POLINOMIAL' else a*s.sqrt(x)+b if tipo=='RADICAL' else a/x**n+b
            formula='(k*x^p)′ = k*p*x^(p−1); constante deriva para zero; a soma deriva termo a termo.'
            passos=[f'Reescreva em potências: {texto(f)}.',
                'Mantenha o coeficiente de cada termo, multiplique pelo expoente e diminua o expoente em 1.',
                *[f'd/dx({texto(v)}) = {texto(s.diff(v,x))}.' for v in s.Add.make_args(f)]]
            dominio='x > 0' if tipo=='RADICAL' else 'x ≠ 0' if tipo=='RACIONAL' else ''
        elif t=='produto':
            u=a*x+b;v=x**n+c if tipo=='POLINOMIAL' else s.sin(x) if tipo=='TRIGONOMETRICA' else s.exp(x)
            f=u*v;formula='(u*v)′ = u′*v + u*v′'
            passos=[f'Separe u = {texto(u)} e v = {texto(v)}.',f'Calcule u′ = {texto(s.diff(u,x))} e v′ = {texto(s.diff(v,x))}.',
                f'Aplique o produto: ({texto(s.diff(u,x))})*({texto(v)}) + ({texto(u)})*({texto(s.diff(v,x))}).']
        elif t=='quociente':
            u=a*x*x+b if tipo=='RACIONAL' else s.sin(x) if tipo=='TRIGONOMETRICA' else s.log(x)
            v=x+c;f=u/v;formula='(u/v)′ = (u′*v − u*v′)/v²'
            passos=[f'Separe u = {texto(u)} e v = {texto(v)}.',f'Calcule u′ = {texto(s.diff(u,x))} e v′ = 1.',
                f'Substitua na regra: (({texto(s.diff(u,x))})*({texto(v)}) − ({texto(u)}))/({texto(v)})².']
            dominio=f'x ≠ {-c}'+('; x > 0' if tipo=='LOGARITMICA' else '')
        elif t=='cadeia':
            u=a*x+b
            f=u**n if tipo=='POLINOMIAL' else s.sqrt(u) if tipo=='RADICAL' else s.sin(u) if tipo=='TRIGONOMETRICA' else s.exp(u) if tipo=='EXPONENCIAL' else s.log(u)
            z=s.Symbol('u');externa=z**n if tipo=='POLINOMIAL' else s.sqrt(z) if tipo=='RADICAL' else s.sin(z) if tipo=='TRIGONOMETRICA' else s.exp(z) if tipo=='EXPONENCIAL' else s.log(z)
            formula='[F(u(x))]′ = F′(u(x))*u′(x)'
            passos=[f'Identifique a interna u(x) = {texto(u)} e a externa F(u) = {texto(externa)}.',
                f'Derive a externa: F′(u) = {texto(s.diff(externa,z))}.',f'Derive a interna: u′(x) = {a}.',
                f'Substitua u e multiplique: ({texto(s.diff(externa,z).subs(z,u))})*{a}.']
            if tipo in {'RADICAL','LOGARITMICA'}: dominio=f'{texto(u)} > 0'
            erros=['Não esqueça de multiplicar pela derivada da função interna.']
        else:
            if t=='trigonometrica':
                f=a*[s.sin(x),s.cos(x),s.tan(x)][int(n)%3];formula='sen′(x)=cos(x); cos′(x)=−sen(x); tg′(x)=sec²(x).'
            elif t=='exponencial': f=a*s.exp(x);formula='(e^x)′ = e^x'
            elif t=='logaritmica': f=a*s.log(x);formula='(ln(x))′ = 1/x';dominio='x > 0'
            else: f=a*s.sinh(x) if n%2 else a*s.cosh(x);formula='senh′(x)=cosh(x); cosh′(x)=senh(x).'
            passos=[f'Identifique a função elementar e o fator constante {a}.',f'Aplique a fórmula: {formula}',f'Multiplique a derivada pelo fator {a}.']
        resposta=s.simplify(s.diff(f,x));pergunta=f'Calcule f′(x), para f(x) = {texto(f)}.'
        passos.append(f'Simplifique: f′(x) = {texto(resposta)}.')
    elif t=='implicita':
        y=s.Symbol('y', real=True);resposta=-x/y
        pergunta=f'Calcule dy/dx para x² + y² = {a*a+b*b}, considerando y ≠ 0.';formula='d/dx(y²) = 2*y*dy/dx'
        passos=['Derive ambos os lados em relação a x: 2*x + 2*y*dy/dx = 0.',
            'Isole o termo com dy/dx: 2*y*dy/dx = −2*x.','Divida por 2*y (y ≠ 0): dy/dx = −x/y.'];dominio='y ≠ 0, sobre a curva dada'
    elif t in {'tangente','taxa','diferencial'}:
        f=a*x*x+b*x+c;der=s.diff(f,x);valor=der.subs(x,c)
        formula='y − f(p) = f′(p)*(x − p)' if t=='tangente' else 'taxa instantânea = f′(p)' if t=='taxa' else 'dy = f′(x)*dx'
        passos=[f'Derive f(x) = {texto(f)}: f′(x) = {texto(der)}.',f'Em x = {c}, f′({c}) = {valor}.']
        if t=='tangente':
            resposta=s.expand(f.subs(x,c)+valor*(x-c));pergunta=f'Calcule a equação da reta tangente a f(x) = {texto(f)} em x = {c}. Informe y em função de x.'
            passos += [f'O ponto é ({c}, {f.subs(x,c)}).',f'Substitua na fórmula: y − {f.subs(x,c)} = {valor}*(x − {c}).']
        elif t=='taxa':
            resposta=valor;pergunta=f'Calcule a taxa de variação instantânea de f(x) = {texto(f)} em x = {c}.'
            passos += [f'Substitua na derivada: {2*a}*{c} + {b} = {valor}.']
        else:
            dx=s.Rational(1,10);resposta=valor*dx;pergunta=f'Calcule dy para f(x) = {texto(f)}, x = {c} e dx = 1/10.'
            passos += [f'Substitua dx: dy = {valor}*(1/10) = {texto(resposta)}.']
    elif t=='crescimento':
        k=s.Rational(1,int(a)+1);sinal=-1 if n%2 else 1
        f=b*s.exp(sinal*k*x);resposta=s.diff(f,x).subs(x,0)
        pergunta=f'Para P(t) = {texto(f).replace("x","t")}, calcule P′(0).';formula='P′(t) = k*P(t) para P(t) = P₀*e^(k*t).'
        passos=[f'A constante de taxa é k = {texto(sinal*k)}.',f'P(0) = {b}.',f'Logo P′(0) = ({texto(sinal*k)})*{b} = {texto(resposta)}.']
    elif t=='relacionadas':
        resposta=2*a*b;pergunta=f'Um quadrado tem lado l(t). No instante considerado, l = {a} cm e dl/dt = {b} cm/s. Calcule dA/dt em cm²/s.'
        formula='A = l²; dA/dt = 2*l*dl/dt'
        passos=['Relacione as grandezas: A(t) = l(t)².','Derive em relação ao tempo usando a cadeia: dA/dt = 2*l*dl/dt.',f'Substitua: 2*{a}*{b} = {resposta} cm²/s.']
    elif t=='linearizacao':
        p=a*a; alvo=p+s.Rational(1,10);resposta=a+s.Rational(1,20)/a
        pergunta=f'Use a linearização de f(x) = sqrt(x) em x = {p} para aproximar sqrt({texto(alvo)}).';formula='L(x) = f(p) + f′(p)*(x − p)'
        passos=[f'f({p}) = {a}.',f'f′(x) = 1/(2*sqrt(x)); f′({p}) = 1/{2*a}.',f'L(x) = {a} + (x − {p})/{2*a}.',f'L({texto(alvo)}) = {texto(resposta)}. É aproximação, não igualdade com a raiz exata.']
    else: raise ValueError('Tópico não implementado.')
    if not isinstance(resposta,str): resposta=s.simplify(resposta)
    certo=resposta if isinstance(resposta,str) else texto(resposta)
    passos.append(f'Resultado: {certo}.')
    if dominio: passos.append(f'Restrição: {dominio}.')
    return dict(enunciado=pergunta,conceito=TOPICOS[t][2],formula=formula,substituicao=passos[0],
        calculos=passos,resolucao='\n\n'.join(f'{i}. {p}' for i,p in enumerate(passos,1)),erros_comuns=erros,
        dica='Consulte a Tabela de Derivadas do Prof. Douglas Maioli: identifique a função e a regra antes de derivar.' if TOPICOS[t][1]==2 else 'Faça o cálculo no papel antes de conferir as alternativas.'), resposta


def construir(spec,rng):
    corpo,valor=elaborar(spec)
    if isinstance(valor,str):
        candidatos=['+∞','−∞','0','1','O limite não existe e os limites laterais têm sinais opostos.'] if spec['topico']=='infinito_ponto' else ['Sim, é contínua.','Não, os limites laterais são diferentes.','Não, f(1) não está definida.','Não, os dois limites laterais são infinitos.','Não é possível calcular nenhum limite lateral.']
        certo=valor
    else:
        certo=texto(valor);candidatos=[certo]
        for delta in [1,-1,2,-2,3,4]:
            extra=s.simplify(valor+delta)
            if texto(extra) not in candidatos: candidatos.append(texto(extra))
            if len(candidatos)==5: break
    rng.shuffle(candidatos)
    return dict(corpo,spec=copy.deepcopy(spec),alternativas=dict(zip('ABCDE',candidatos)),gabarito='ABCDE'[candidatos.index(certo)],fingerprint=fingerprint(spec))


def verificar(q):
    corpo,valor=elaborar(q['spec']); certo=valor if isinstance(valor,str) else texto(valor)
    if (set(q['alternativas'])!=set('ABCDE') or len(set(q['alternativas'].values()))!=5
            or q['alternativas'].get(q['gabarito'])!=certo or sum(v==certo for v in q['alternativas'].values())!=1
            or q['fingerprint']!=fingerprint(q['spec']) or any(q.get(k)!=v for k,v in corpo.items())):
        raise ValueError('Questão de Cálculo diverge do cálculo simbólico e das etapas conferidas.')
    return True


def gerar(slug,referencias,quantidade,excluidos,unidade=0,topico='MISTO',tipo_funcao='MISTO'):
    if not referencias or any(r.get('disciplina_slug')!='calculo_para_computacao_1' for r in referencias): return []
    opcoes=[t for t,v in TOPICOS.items() if v[0]==slug and (not unidade or v[1]==unidade)
        and (topico=='MISTO' or topico==t) and (tipo_funcao=='MISTO' or tipo_funcao in v[3])]
    opcoes=[t for t in opcoes if any(fonte_compativel(t,r) for r in referencias)]
    rng=random.Random(secrets.randbits(128));vistos=set(excluidos);questoes=[]
    for _ in range(quantidade*40):
        if len(questoes)==quantidade or not opcoes: break
        t=rng.choice(opcoes);tipo=rng.choice(TOPICOS[t][3]) if tipo_funcao=='MISTO' else tipo_funcao
        spec=dict(motor='calculo',topico=t,tipo_funcao=tipo,parametros=[rng.randint(1,9),rng.randint(1,9),rng.randint(2,5),rng.randint(1,9)])
        if fingerprint(spec) in vistos:continue
        fontes=[r for r in referencias if r['assunto_principal_proposto']==slug and fonte_compativel(t,r)
            and (not all(f.get('arquivo','').startswith('prova') for f in r['fontes'])
                or tipo in {'POLINOMIAL','RACIONAL','POR_PARTES','AFIM'})]
        # O treino de fatoração usa a questão 5 da UP1 como referência.
        if not fontes:continue
        ref=rng.choice(fontes);q=construir(spec,rng)
        q.update(origem='GERADA_IA',fontes=ref['fontes'],resolucao_gerada_por_ia=True,
            origem_gabarito='GERADO_IA_CONFERIDO_SIMBOLICAMENTE',
            aviso='Exercício inédito de estudo, com comando direto e cálculo conferido. Não é questão oficial. '+
                ('Derivadas: 2ª unidade. A prova desta unidade ainda não foi fornecida. Consulte a Tabela de Derivadas do Prof. Douglas Maioli.' if TOPICOS[t][1]==2 else 'A prova disponível é da 1ª unidade; as alternativas são apoio para conferir seu cálculo.'))
        verificar(q);questoes.append(q);vistos.add(q['fingerprint'])
    return questoes
