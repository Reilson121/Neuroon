"""Exercícios de Estatística com cálculo verificável, sem executar texto do LLM.

Famílias distintas cobrem os conceitos presentes nas avaliações disponíveis.
O modelo cria o contexto narrativo; os dados, condições, alternativas e
resolução matemática são montados e conferidos por este componente.
"""

import hashlib
import json
import math
import statistics
from fractions import Fraction as F

FAMILIAS = {
    "fundamentos_de_probabilidade": ["espaco_amostral", "uniao", "complemento"],
    "analise_combinatoria": ["arranjo", "combinacao", "permutacao"],
    "probabilidade_condicional_e_independencia": ["condicional", "sem_reposicao"],
    "medidas_de_tendencia_central": ["media", "mediana", "media_ponderada", "valor_ausente", "robustez"],
    "medidas_de_dispersao_e_posicao": ["amplitude", "variancia_populacional", "variancia_amostral", "desvio_padrao", "iqr"],
    "correlacao_e_associacao": ["correlacao", "interpretacao_correlacao"],
}


def quantil(valores, q):
    x = sorted(map(F, valores))
    h = (len(x) - 1) * F(q)
    i = h.numerator // h.denominator
    return x[i] + (h - i) * (x[min(i + 1, len(x) - 1)] - x[i])


def calcular(spec):
    k, d = spec["familia"], spec["dados"]
    x = list(map(F, d.get("valores", [])))
    if k == "media": return sum(x) / len(x)
    if k == "mediana": return F(statistics.median(sorted(x)))
    if k == "media_ponderada": return sum(F(a) * b for a, b in zip(d["valores"], d["frequencias"])) / sum(d["frequencias"])
    if k == "valor_ausente": return F(d["media_alvo"]) * (len(x) + 1) - sum(x)
    if k == "amplitude": return max(x) - min(x)
    if k in {"variancia_populacional", "variancia_amostral", "desvio_padrao"}:
        v = statistics.variance(x) if k == "variancia_amostral" else statistics.pvariance(x)
        return math.sqrt(float(v)) if k == "desvio_padrao" else F(v)
    if k == "iqr": return quantil(x, F(3, 4)) - quantil(x, F(1, 4))
    if k == "espaco_amostral": return F(math.prod(d["possibilidades"]))
    if k == "uniao": return F(d["a"] + d["b"] - d["ambos"], d["total"])
    if k == "complemento": return F(d["total"] - d["evento"], d["total"])
    if k == "arranjo": return F(math.perm(d["n"], d["k"]))
    if k == "combinacao": return F(math.comb(d["n"], d["k"]))
    if k == "permutacao": return F(math.factorial(d["n"]))
    if k == "condicional": return F(d["ambos"], d["condicao"])
    if k == "sem_reposicao": return F(d["azuis"], d["total"]) * F(d["vermelhas"], d["total"] - 1)
    if k == "robustez":
        novo = x[:-1] + [x[-1] + d["acrescimo"]]
        if statistics.median(x) == statistics.median(novo) and statistics.mean(novo) > statistics.mean(x):
            return "A mediana permanece igual e a média aumenta."
        raise ValueError("Cenário de robustez não verificado.")
    if k in {"correlacao", "interpretacao_correlacao"}:
        y = list(map(F, d["y"]))
        mx, my = sum(x) / len(x), sum(y) / len(y)
        numerador = sum((a - mx) * (b - my) for a, b in zip(x, y))
        denominador = math.sqrt(float(sum((a - mx)**2 for a in x) * sum((b - my)**2 for b in y)))
        r = float(numerador) / denominador
        if k == "correlacao": return r
        if math.isclose(r, 1, abs_tol=1e-10): return "Associação linear positiva perfeita nos dados."
        if math.isclose(r, -1, abs_tol=1e-10): return "Associação linear negativa perfeita nos dados."
        if math.isclose(r, 0, abs_tol=1e-10): return "Ausência de associação linear nos dados, sem garantir independência."
        raise ValueError("Interpretação fora das categorias verificadas.")
    raise ValueError("Família matemática não suportada.")


def mostrar(v):
    if isinstance(v, str): return v
    if isinstance(v, F): return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return f"{v:.2f}".replace(".", ",")


def criar_spec(familia, rng):
    x = sorted(rng.sample(range(2, 24), rng.choice([5, 6, 7, 8])))
    d = {"valores": x}
    if familia == "media_ponderada": d = {"valores": rng.sample(range(2, 12), 4), "frequencias": [rng.randint(1, 5) for _ in range(4)]}
    if familia == "valor_ausente": d = {"valores": x[:4], "media_alvo": rng.randint(max(12, math.ceil(sum(x[:4])/5)+1), 25)}
    if familia == "robustez": d["acrescimo"] = rng.randint(20, 80)
    if familia == "espaco_amostral": d = {"possibilidades": [rng.randint(2, 5) for _ in range(rng.choice([2, 3]))]}
    if familia in {"uniao", "complemento", "condicional"}:
        n = rng.randint(12, 30); a = rng.randint(4, n - 3); b = rng.randint(3, n - 2)
        ambos = rng.randint(max(1, a+b-n), min(a, b)-1)
        d = {"total": n, "a": a, "b": b, "ambos": ambos, "evento": a, "condicao": b}
    if familia in {"arranjo", "combinacao"}: d = {"n": rng.randint(6, 12), "k": rng.choice([2, 3, 4])}
    if familia == "permutacao": d = {"n": rng.randint(4, 8)}
    if familia == "sem_reposicao":
        azul, vermelho = rng.randint(3, 9), rng.randint(3, 9)
        d = {"azuis": azul, "vermelhas": vermelho, "total": azul+vermelho}
    if familia in {"correlacao", "interpretacao_correlacao"}:
        x = [-2, -1, 0, 1, 2]; inclinacao = rng.choice([-3, -2, 1, 2, 3]); intercepto = rng.randint(5, 20)
        y = [inclinacao*a+intercepto for a in x] if rng.choice([True, False]) else [a*a+intercepto for a in x]
        d = {"valores": x, "y": y}
    return {"familia": familia, "dados": d}


def elaborar(spec):
    k, d = spec["familia"], spec["dados"]
    valor = calcular(spec)
    x = d.get("valores", [])
    dados = f"Dados observados: {x}." if x else ""
    conceito = k.replace("_", " ").capitalize()
    formula, pergunta, passos, erros = "", "", [], []
    if k in {"media", "mediana", "amplitude"}:
        formula = {"media": "média = soma dos valores / n", "mediana": "mediana = valor central dos dados ordenados; para n par, média dos dois centrais", "amplitude": "R = máximo − mínimo"}[k]
        pergunta = {"media": "Qual é a média aritmética?", "mediana": "Qual é a mediana?", "amplitude": "Qual é a amplitude?"}[k]
        passos = [f"Ordenando: {sorted(x)}.", f"Quantidade n={len(x)}; soma={sum(x)}; mínimo={min(x)}; máximo={max(x)}."]
        if k == "mediana":
            meio = len(x)//2
            ordenados = sorted(x)
            passos.append(f"Centro: {ordenados[meio]} (n ímpar)." if len(x)%2 else f"Centrais: {ordenados[meio-1]} e {ordenados[meio]}; média dos dois = {mostrar(valor)}.")
        if k == "media": passos.append(f"Média={sum(x)}/{len(x)}={mostrar(valor)}.")
        if k == "amplitude": passos.append(f"R={max(x)}−{min(x)}={mostrar(valor)}.")
        erros = ["Não confunda média, mediana e moda.", "Para a mediana, ordene os dados antes de procurar o centro."]
    elif k == "media_ponderada":
        dados = "Tabela de valores e frequências:\n| Valor | Frequência |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a,b in zip(x,d["frequencias"]))
        pergunta = "Qual é a média, considerando as frequências?"; formula = "média ponderada = Σ(valor × frequência) / Σ(frequência)"
        passos = [f"Produtos: {[a*b for a,b in zip(x,d['frequencias'])]}.", f"Soma ponderada={sum(a*b for a,b in zip(x,d['frequencias']))}; soma das frequências={sum(d['frequencias'])}."]
        erros = ["Divida pela soma das frequências, não pelo número de linhas."]
    elif k == "valor_ausente":
        dados = f"Há {len(x)+1} observações. São conhecidas {x}; a média de todas deve ser {d['media_alvo']}."
        pergunta = "Qual deve ser o valor da observação ausente?"; formula = "valor ausente = média desejada × n − soma dos conhecidos"
        passos = [f"Soma necessária={d['media_alvo']} × {len(x)+1}={d['media_alvo']*(len(x)+1)}.", f"Soma conhecida={sum(x)}."]
        erros = ["Não divida apenas a soma dos conhecidos: a média informada inclui a observação ausente."]
    elif k in {"variancia_populacional", "variancia_amostral", "desvio_padrao"}:
        amostral = k == "variancia_amostral"; n = len(x); media = sum(map(F,x))/n
        quadrados = [(F(a)-media)**2 for a in x]; den = n-1 if amostral else n
        pergunta = "Qual é a variância amostral?" if amostral else "Qual é o desvio-padrão populacional, arredondado para duas casas decimais?" if k=="desvio_padrao" else "Qual é a variância populacional?"
        dados += " Trate o conjunto como uma amostra." if amostral else " Trate o conjunto como a população inteira."
        formula = "s² = Σ(x − média)²/(n−1)" if amostral else "σ = sqrt(Σ(x − média)²/n)" if k=="desvio_padrao" else "σ² = Σ(x − média)²/n"
        passos = [f"Média={mostrar(media)}.", f"Quadrados dos desvios: {[mostrar(v) for v in quadrados]}.", f"Soma dos quadrados={mostrar(sum(quadrados))}; denominador={den}.", f"Variância={mostrar(sum(quadrados)/den)}."]
        if k == "desvio_padrao": passos.append(f"Desvio-padrão=sqrt({mostrar(sum(quadrados)/den)})≈{mostrar(valor)}.")
        erros = ["Use n na população e n−1 na variância amostral.", "O desvio-padrão é a raiz da variância, não a própria variância."]
    elif k == "iqr":
        pergunta = "Qual é o intervalo interquartil (IQR)?";formula = "h=(n−1)q, índice iniciado em zero, interpolação linear; IQR=Q3−Q1"
        dados += " Para os quartis, use h=(n−1)q, com índice iniciado em zero e interpolação linear entre os valores vizinhos."
        passos = [f"Dados ordenados={x}."]
        for q in [F(1,4),F(3,4)]:
            h=(len(x)-1)*q;i=h.numerator//h.denominator
            passos.append(f"q={mostrar(q)}: h={mostrar(h)}; vizinhos nos índices {i} e {min(i+1,len(x)-1)}; quartil={mostrar(quantil(x,q))}.")
            j=min(i+1,len(x)-1)
            passos.append(f"Interpolação: {x[i]}+{mostrar(h-i)}×({x[j]}−{x[i]})={mostrar(quantil(x,q))}.")
        passos.append(f"IQR={mostrar(quantil(x,F(3,4)))}−{mostrar(quantil(x,F(1,4)))}={mostrar(valor)}.")
        erros = ["Não use (n+1)q nesta questão: ela pede a convenção com índice zero.", "Subtraia Q1 de Q3, não a mediana."]
    elif k == "robustez":
        dados += f" Substitua somente o maior valor por {x[-1]+d['acrescimo']}, mantendo os outros dados."
        pergunta = "O que acontece com a média e a mediana?";formula = "média=Σx/n; mediana=centro dos dados ordenados"
        novo=x[:-1]+[x[-1]+d['acrescimo']]
        passos = [f"Média antes={mostrar(F(sum(x),len(x)))}; depois={mostrar(F(sum(novo),len(novo)))}.", f"Mediana antes={statistics.median(x)}; depois={statistics.median(novo)}."]
        erros = ["Um extremo pode alterar muito a média sem alterar a posição central."]
    elif k == "espaco_amostral":
        dados = f"Um resultado é uma sequência de escolhas. As etapas têm, respectivamente, {d['possibilidades']} opções. Todas as combinações são permitidas."
        pergunta = "Quantos resultados distintos há no espaço amostral?";formula = "total = produto do número de opções de cada etapa"
        passos = ["Multiplique, não some, as possibilidades de etapas sucessivas."]
        erros = ["Somar as opções não conta todas as sequências possíveis."]
    elif k in {"uniao", "complemento", "condicional"}:
        dados = f"São {d['total']} registros: {d['a']} têm A, {d['b']} têm B e {d['ambos']} têm ambos. Um registro é sorteado uniformemente."
        if k == "uniao":
            pergunta="Qual é a probabilidade de o registro ter A ou B, incluindo ambos?";formula="P(A∪B)=(n(A)+n(B)−n(A∩B))/N";passos=[f"Contagem da união={d['a']}+{d['b']}−{d['ambos']}={d['a']+d['b']-d['ambos']}."]
        elif k == "complemento":
            pergunta="Qual é a probabilidade de o registro não ter A?";formula="P(Aᶜ)=1−P(A)";passos=[f"Sem A={d['total']}−{d['a']}={d['total']-d['a']}."]
        else:
            pergunta="Sabendo que o registro tem B, qual é a probabilidade de também ter A?";formula="P(A|B)=n(A∩B)/n(B)";passos=[f"O universo condicionado tem {d['b']} registros; destes, {d['ambos']} também têm A."]
        erros=["Na condicional, o denominador é o grupo condicionado; na união, desconte a interseção."]
    elif k in {"arranjo", "combinacao", "permutacao"}:
        n=d['n'];m=d.get('k',n)
        dados=f"Há {n} pessoas distintas disponíveis."
        if k=='arranjo':pergunta=f"De quantas formas é possível preencher {m} funções diferentes, sem acumular funções?";formula="A(n,k)=n!/(n−k)!"
        elif k=='combinacao':pergunta=f"Quantos grupos de {m} pessoas podem ser formados, sem função ou ordem entre integrantes?";formula="C(n,k)=n!/[k!(n−k)!]"
        else:pergunta="De quantas formas todas as pessoas podem ser ordenadas numa fila?";formula="P(n)=n!"
        passos=[f"n={n}; elementos escolhidos={m}.", "A ordem importa nas funções e na fila; não importa em grupos sem funções."]
        if k=='arranjo': passos.append(f"A({n},{m})={math.factorial(n)}/{math.factorial(n-m)}={mostrar(valor)}.")
        elif k=='combinacao': passos.append(f"C({n},{m})={math.factorial(n)}/({math.factorial(m)}×{math.factorial(n-m)})={mostrar(valor)}.")
        else: passos.append(f"{n}!="+'×'.join(map(str,range(n,0,-1)))+f"={mostrar(valor)}.")
        erros=["Distinguir grupo sem ordem de atribuição a funções diferentes evita confundir combinação e arranjo."]
    elif k == 'sem_reposicao':
        dados=f"Uma caixa tem {d['azuis']} fichas azuis e {d['vermelhas']} vermelhas. Retiram-se duas fichas uniformemente, em sequência, sem reposição."
        pergunta="Qual é a probabilidade de a primeira ser azul e a segunda vermelha?";formula="P(azul depois vermelha)=(azuis/N)×(vermelhas/(N−1))"
        passos=[f"Primeira retirada: {d['azuis']}/{d['total']}.",f"Após retirar uma azul, permanecem {d['vermelhas']} vermelhas entre {d['total']-1} fichas."]
        erros=["Sem reposição, o total da segunda retirada é N−1."]
    elif k in {'correlacao','interpretacao_correlacao'}:
        dados="Tabela de observações:\n| X | Y |\n|---|---|\n"+'\n'.join(f"| {a} | {b} |" for a,b in zip(x,d['y']))
        pergunta="Qual é o coeficiente de correlação de Pearson, arredondado para duas casas decimais?" if k=='correlacao' else "Qual interpretação é sustentada pelo coeficiente de correlação desses dados?"
        formula="r = Σ[(x−médiaX)(y−médiaY)] / sqrt(Σ(x−médiaX)² × Σ(y−médiaY)²)"
        mx=F(sum(x),len(x));my=F(sum(d['y']),len(x))
        sxy=sum((F(a)-mx)*(F(b)-my) for a,b in zip(x,d['y']));sxx=sum((F(a)-mx)**2 for a in x);syy=sum((F(b)-my)**2 for b in d['y'])
        passos=[f"MédiaX={mostrar(mx)}; médiaY={mostrar(my)}.",f"Soma dos produtos={mostrar(sxy)}; somas dos quadrados={mostrar(sxx)} e {mostrar(syy)}."]
        r = calcular({"familia":"correlacao","dados":d})
        passos.append(f"r={mostrar(sxy)}/sqrt({mostrar(sxx)}×{mostrar(syy)})={mostrar(r)}.")
        erros=["Correlação não prova causalidade; correlação zero não garante independência."]
    else: raise ValueError("Família sem resolução didática.")
    substituicao=' '.join(passos)
    return {"enunciado":dados+'\n\n'+pergunta,"conceito":conceito,"formula":formula,"substituicao":substituicao,
            "calculos":[*passos,f"Resultado: {mostrar(valor)}."],"resolucao":f"Aplicando {formula}, obtemos {mostrar(valor)}.",
            "erros_comuns":erros,"dica":"Identifique os dados, a condição e a fórmula antes de calcular. Confira a convenção e arredonde apenas no final."}


def construir(familia,rng):
    spec=criar_spec(familia,rng); valor=calcular(spec);certo=mostrar(valor)
    if isinstance(valor,str):
        candidatos = ["A mediana permanece igual e a média aumenta.","A média permanece igual e a mediana aumenta.","As duas permanecem iguais.","A média diminui e a mediana permanece igual.","As duas diminuem."] if familia=='robustez' else ["Associação linear positiva perfeita nos dados.","Associação linear negativa perfeita nos dados.","Ausência de associação linear nos dados, sem garantir independência.","Os dados comprovam uma relação causal.","A independência entre as variáveis está garantida."]
    else:
        candidatos=[certo]; prob=familia in {'uniao','condicional','complemento','sem_reposicao'}
        if familia == 'correlacao': extras=[-1.0,-0.5,0.0,0.5,1.0]
        elif familia in {'arranjo','combinacao','permutacao','espaco_amostral'}:
            n=spec['dados'].get('n',5);k=spec['dados'].get('k',2)
            extras=[F(math.comb(n,k)),F(n**k),F(n*k),F(math.factorial(n)),valor+1,valor+2,valor+3]
        elif prob:
            extras=[1-valor,valor/2,valor/3,valor*2,valor*3,*[F(i,12) for i in range(13)]]
        else:extras=[valor+1,valor+2,valor/2,valor*2,valor+3,valor+4,valor+5]
        for v in extras:
            text=mostrar(v)
            if text not in candidatos and (not prob or 0<=v<=1):candidatos.append(text)
            if len(candidatos)==5:break
    if len(candidatos)!=5:raise ValueError('Alternativas insuficientes.')
    rng.shuffle(candidatos);alternativas=dict(zip('ABCDE',candidatos));gabarito=next(k for k,v in alternativas.items() if v==certo)
    q={**elaborar(spec),'spec':spec,'alternativas':alternativas,'gabarito':gabarito,
       'fingerprint':hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()}
    if familia in {'media','amplitude'}:
        q['visualizacao']={'tipo':'barras','titulo':'Valores observados','rotulos':[str(i+1) for i in range(len(spec['dados']['valores']))],
                          'valores':spec['dados']['valores']}
    elif familia in {'correlacao','interpretacao_correlacao'}:
        q['visualizacao']={'tipo':'dispersao','titulo':'Observações de X e Y','x':spec['dados']['valores'],'y':spec['dados']['y']}
    verificar(q)
    return q


def verificar(q):
    if q.get('spec', {}).get('motor') == 'estrutura_de_dados_avancada':
        from app.practice.ed_avancada_engine import verificar as verificar_avancada
        return verificar_avancada(q)
    if q.get('spec', {}).get('motor') == 'design_de_artefatos_digitais':
        from app.practice.design_engine import verificar as verificar_design
        return verificar_design(q)
    if q.get('spec', {}).get('motor') == 'calculo':
        from app.practice.calculo_engine import verificar as verificar_calculo
        return verificar_calculo(q)
    if q.get('spec', {}).get('motor') == 'estrutura_de_dados':
        from app.practice.ed_basica_engine import verificar as verificar_ed
        return verificar_ed(q)
    if q.get('spec', {}).get('motor') == 'sistemas_digitais':
        from app.practice.digital_engine import verificar as verificar_digitais
        return verificar_digitais(q)
    correto=mostrar(calcular(q['spec']))
    if set(q['alternativas'])!=set('ABCDE') or len(set(q['alternativas'].values()))!=5:
        raise ValueError('Alternativas ambíguas ou repetidas.')
    if sum(v==correto for v in q['alternativas'].values())!=1 or q['alternativas'].get(q['gabarito'])!=correto:
        raise ValueError('Gabarito não confere com o cálculo independente.')
    return True
