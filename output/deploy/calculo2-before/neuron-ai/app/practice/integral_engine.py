"""Integrais diretas: unidade 1 univariada; unidade 2 iteradas cartesianas."""
import copy
import hashlib
import random
import secrets
import sympy as s

DISCIPLINA = 'calculo_para_computacao_2'
X,Y,Z = s.symbols('x y z', real=True)
TIPOS = ['POLINOMIAL','RADICAL','RACIONAL','TRIGONOMETRICA','EXPONENCIAL']
TOPICOS = {
 'primitiva': ('primitivas',1,'Primitivas e constante de integração',['POLINOMIAL']),
 'integral_direta': ('integrais_indefinidas',1,'Integração direta pela tabela',TIPOS),
 'integral_definida': ('integrais_definidas',1,'Integral definida e F(b) - F(a)',TIPOS),
 'dupla_retangulo': ('integrais_duplas_retangulares',2,'Integral dupla em retângulo',['POLINOMIAL']),
 'dupla_iterada': ('integrais_duplas_iteradas',2,'Integral dupla com limite variável',['POLINOMIAL']),
 'tripla_caixa': ('integrais_triplas_retangulares',2,'Integral tripla em caixa',['POLINOMIAL']),
 'tripla_iterada': ('integrais_triplas_iteradas',2,'Integral tripla com limites variáveis',['POLINOMIAL']),
 'valor_multivariavel': ('base_multivariavel',0,'Complemento opcional: valor de função',['POLINOMIAL']),
}

def texto(v):
    return s.sstr(v).replace('**','^').replace('sin(', 'sen(').replace('log(', 'ln(')

def elaborar(spec):
    t=spec['topico'];tipo=spec['tipo_funcao'];a,b,n,c=map(s.Integer,spec['parametros'])
    if t not in TOPICOS or tipo not in TOPICOS[t][3] or not(1<=a<=30 and 1<=b<=30 and 2<=n<=5 and 1<=c<=30):
        raise ValueError('Parâmetros de integral inválidos.')
    x,y,z=X,Y,Z; passos=[]; indef=t in {'primitiva','integral_direta'}
    formula=''; expr=None; limites=[]
    if t in {'primitiva','integral_direta','integral_definida'}:
        f={'POLINOMIAL':a*x**n+b*x+c,'RADICAL':a*s.sqrt(x)+b,
           'RACIONAL':a/x,'TRIGONOMETRICA':a*s.sin(x)+b*s.cos(x),
           'EXPONENCIAL':a*s.exp(x)}[tipo]
        # x>0 para log(x); a tabela explica a extensão ln|x| em x<0.
        prim={'POLINOMIAL':a*x**(n+1)/(n+1)+b*x*x/2+c*x,
              'RADICAL':2*a*x**s.Rational(3,2)/3+b*x,'RACIONAL':a*s.log(x),
              'TRIGONOMETRICA':-a*s.cos(x)+b*s.sin(x),'EXPONENCIAL':a*s.exp(x)}[tipo]
        expr=f
        formula='∫ x^p dx = x^(p+1)/(p+1) + C (p ≠ -1); linearidade e tabela de integrais.'
        passos=[f'Identifique o integrando: {texto(f)}.',f'Integre termo a termo pela tabela: F(x) = {texto(prim)}.',
                f'Confira por derivação: F′(x) = {texto(s.simplify(s.diff(prim,x)))}.']
        if indef:
            pergunta=f'Calcule ∫ ({texto(f)}) dx'+(' no intervalo x > 0.' if tipo=='RACIONAL' else '.')
            valor=prim
            passos.append('Acrescente a constante C, pois a derivada de qualquer constante é zero.')
        else:
            lo=s.Integer(1) if tipo=='RACIONAL' else s.Integer(0);hi=s.Integer(2)
            limites=[(x,lo,hi)]
            pergunta=f'Calcule ∫ de {lo} a {hi} ({texto(f)}) dx.'
            valor=s.simplify(prim.subs(x,hi)-prim.subs(x,lo))
            formula='Teorema Fundamental do Cálculo: ∫ de a a b f(x) dx = F(b) - F(a), para f contínua em [a,b].'
            passos += [f'F({hi}) = {texto(prim.subs(x,hi))}; F({lo}) = {texto(prim.subs(x,lo))}.',
                       f'Subtraia o valor inferior do superior: {texto(valor)}. A constante se cancela.']
        if tipo=='RACIONAL':passos.append('Domínio deste exercício: x > 0. Em geral ∫1/x dx = ln|x| + C em cada intervalo sem zero.')
        if tipo=='RADICAL':passos.append('Domínio real: x ≥ 0; use sqrt(x) = x^(1/2).')
    elif t.startswith(('dupla','tripla')):
        expr=a*x+b*y+(c*z if t.startswith('tripla') else c)
        if t=='dupla_retangulo':limites=[(y,0,2),(x,0,1)]
        elif t=='dupla_iterada':limites=[(y,0,x),(x,0,2)]
        elif t=='tripla_caixa':limites=[(z,0,1),(y,0,2),(x,0,1)]
        else:limites=[(z,0,x+y),(y,0,x),(x,0,1)]
        notacao=' '.join(f'∫ de {texto(lo)} a {texto(hi)}' for v,lo,hi in reversed(limites))
        diferenciais=' '.join('d'+str(v) for v,_,_ in limites)
        pergunta=f'Calcule {notacao} ({texto(expr)}) {diferenciais}.'
        formula='Integre de dentro para fora, conforme os diferenciais; as outras variáveis ficam constantes em cada etapa.'
        passos=[f'Ordem de integração: {", depois ".join(str(v) for v,_,_ in limites)}.']
        valor=expr
        for v,lo,hi in limites:
            prim=s.integrate(valor,v)
            passos += [f'Em relação a {v}, uma primitiva de {texto(valor)} é {texto(prim)}.',
                       f'Aplique os limites {texto(lo)} e {texto(hi)}: ({texto(prim.subs(v,hi))}) - ({texto(prim.subs(v,lo))}).']
            valor=s.simplify(prim.subs(v,hi)-prim.subs(v,lo))
            passos.append(f'Resultado desta etapa: {texto(valor)}.')
        passos.append('As integrais internas são definidas; não acrescente constantes C nas etapas.')
    elif t=='valor_multivariavel':
        expr=a*x*x+b*y+c*z;valor=expr.subs({x:1,y:2,z:3})
        pergunta=f'Complemento opcional. Dada f(x,y,z) = {texto(expr)}, calcule f(1,2,3).'
        formula='Substitua simultaneamente cada coordenada na variável correspondente.'
        passos=[f'x=1, y=2 e z=3.',f'f(1,2,3) = {a}*1^2 + {b}*2 + {c}*3.',f'Efetue as operações: {texto(valor)}.']
    valor=s.simplify(valor);certo=texto(valor)+(' + C' if indef else '')
    passos.append('Resultado: '+certo+'.')
    return dict(enunciado=pergunta,conceito=TOPICOS[t][2],formula=formula,substituicao=passos[0],
        calculos=passos,resolucao='\n\n'.join(f'{i}. {p}' for i,p in enumerate(passos,1)),
        erros_comuns=['Não confunda integral definida com primitiva; confira sinais, expoentes e limites.',
                      'Na integração iterada, conserve as demais variáveis e respeite a ordem dos diferenciais.'],
        dica='Consulte a Tabela de Integrais - apoio NEURON e faça os cálculos no papel.'),valor,expr,limites

def fingerprint(spec):
    return hashlib.sha256(elaborar(spec)[0]['enunciado'].encode()).hexdigest()

def construir(spec,rng):
    corpo,valor,_,_=elaborar(spec);indef=spec['topico'] in {'primitiva','integral_direta'}
    # Somar uma constante produziria outra primitiva correta: distratores mudam a derivada.
    candidatos=[texto(valor if d==0 else s.expand(valor+d*X) if indef else s.simplify(valor+d))+(' + C' if indef else '') for d in [0,1,-1,2,-2]]
    certo=candidatos[0];rng.shuffle(candidatos)
    return dict(corpo,spec=copy.deepcopy(spec),alternativas=dict(zip('ABCDE',candidatos)),gabarito='ABCDE'[candidatos.index(certo)],fingerprint=fingerprint(spec))

def verificar(q):
    corpo,valor,expr,limites=elaborar(q['spec']);indef=q['spec']['topico'] in {'primitiva','integral_direta'}
    if indef and s.simplify(s.diff(valor,X)-expr)!=0:raise ValueError('Primitiva incorreta.')
    if limites and s.simplify(s.integrate(expr,*limites)-valor)!=0:raise ValueError('Integral incorreta.')
    certo=texto(valor)+(' + C' if indef else '')
    esperadas={texto(valor if d==0 else s.expand(valor+d*X) if indef else s.simplify(valor+d))+(' + C' if indef else '') for d in [0,1,-1,2,-2]}
    if (q['spec'].get('motor')!='integral' or set(q['alternativas'])!=set('ABCDE') or
        set(q['alternativas'].values())!=esperadas or q['alternativas'].get(q['gabarito'])!=certo or
        q['fingerprint']!=fingerprint(q['spec']) or any(q.get(k)!=v for k,v in corpo.items())):
        raise ValueError('Questão de integral diverge da solução conferida.')
    return True

def gerar(slug,referencias,quantidade,excluidos,unidade=0,topico='MISTO',tipo_funcao='MISTO'):
    if not referencias or any(r.get('disciplina_slug')!=DISCIPLINA for r in referencias):return []
    opcoes=[(t,tipo) for t,v in TOPICOS.items() if v[0]==slug and (not unidade or v[1]==unidade)
            and (topico=='MISTO' or t==topico) for tipo in v[3] if tipo_funcao in {'MISTO',tipo}]
    # Prática curricular somente com fontes autorais de integração; o PDF complementar
    # não serve de prova de que o professor cobra todos os seus capítulos.
    refs=[r for r in referencias if r['assunto_principal_proposto']==slug and any(
        f['arquivo']=='Guia de Integrais - NEURON.pdf' or slug=='base_multivariavel' and f['arquivo']=='funçoes cde duas variaveis.pdf' for f in r['fontes'])]
    if not opcoes or not refs:return []
    rng=random.Random(secrets.randbits(128));pares=[(a,b) for a in range(1,31) for b in range(1,31)];rng.shuffle(pares)
    resultado=[];vistos=set(excluidos)
    for i,(a,b) in enumerate(pares):
        t,tipo=opcoes[i%len(opcoes)]
        spec=dict(motor='integral',topico=t,tipo_funcao=tipo,parametros=[a,b,rng.randint(2,5),(a+b)%30+1])
        if fingerprint(spec) in vistos:continue
        q=construir(spec,rng);q.update(origem='GERADA_IA',fontes=copy.deepcopy(rng.choice(refs)['fontes']),
            resolucao_gerada_por_ia=True,origem_gabarito='GERADO_IA_CONFERIDO_SIMBOLICAMENTE',
            aviso='Exercício autoral de estudo. A disciplina não tem prova oficial; o simulado adapta comandos diretos de Cálculo I. Consulte a tabela de integrais.')
        verificar(q);resultado.append(q);vistos.add(q['fingerprint'])
        if len(resultado)==quantidade:break
    return resultado
