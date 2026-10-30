"""Apresentação LaTeX, separada dos valores e gabaritos conferidos.

O pequeno parser só imprime operações: não usa eval/sympify nem executa texto.
Os identificadores e funções aceitos são explícitos; prosa e Markdown persistem.
"""
import copy
import re
import sympy as s

NAMES=set('x y z a b c n N p k h f g u v F P A B C R Q r l t dx dy dz xi yi Sx Sy finv ginv'.split())
FUNCTIONS={'sqrt':r'\sqrt','sen':r'\sin','sin':r'\sin','cos':r'\cos','tan':r'\tan','tg':r'\tan','ln':r'\ln','log':r'\ln','exp':r'\exp','sinh':r'\sinh','cosh':r'\cosh'}
SYMBOLS={'∞':r'\infty','μ':r'\mu','σ':r'\sigma','Σ':r'\sum','∩':r'\cap','∪':r'\cup','≤':r'\le','≥':r'\ge','≠':r'\ne','≈':r'\approx','→':r'\to'}
TOKEN=re.compile(r'\d+(?:[.,]\d+)?|[^\W\d]\w*[′]?|[∞μσΣ]|\*\*|[^\s]',re.UNICODE)
PREC={'=':1,'≠':1,'≤':1,'≥':1,'<':1,'>':1,'≈':1,'→':1,'∩':2,'∪':2,'+':3,'-':3,'*':4,'×':4,'/':4,'^':6,'**':6}

class Parser:
 def __init__(self,tokens,start):self.ts=tokens;self.i=start
 def peek(self):return self.ts[self.i].group() if self.i<len(self.ts) else ''
 def expr(self,minimum=0):
  token=self.peek();self.i+=1
  if token in {'+','-'}:left=token+self.expr(5)
  elif token=='(':
   left=self.expr()
   if self.peek()!=')':raise ValueError()
   self.i+=1;left=r'\left('+left+r'\right)'
  elif re.fullmatch(r'\d+(?:[.,]\d+)?',token):left=token.replace(',',r'{,}')
  elif token in FUNCTIONS or token.rstrip('′') in NAMES:
   left=FUNCTIONS.get(token,{'finv':r'f^{-1}','ginv':r'g^{-1}','xi':'x_i','yi':'y_i','Sx':'S_x','Sy':'S_y'}.get(token,token.replace('′',r'^{\prime}')))
   if self.peek()=='(':
    self.i+=1;args=[self.expr()];separators=[]
    while self.peek() in {',','|'}:
     separators.append(r'\mid' if self.peek()=='|' else ',')
     self.i+=1;args.append(self.expr())
    if self.peek()!=')':raise ValueError()
    self.i+=1
    value=args[0]+''.join(' '+sep+' '+arg for sep,arg in zip(separators,args[1:]))
    left=r'\sqrt{'+value+'}' if token=='sqrt' else left+r'\left('+value+r'\right)'
  elif token in SYMBOLS:left=SYMBOLS[token]
  else:raise ValueError()
  while self.i<len(self.ts):
   op=self.peek()
   if op=='!':self.i+=1;left+="!";continue
   priority=PREC.get(op,-1)
   if priority<minimum:break
   save=self.i;self.i+=1
   try:right=self.expr(priority if op in {'^','**'} else priority+1)
   except ValueError:self.i=save;break
   if op=='/':left=r'\dfrac{'+left+'}{'+right+'}'
   elif op in {'^','**'}:left='{'+left+'}^{'+right+'}'
   else:left+=' '+({'*':r'\cdot','×':r'\cdot'}.get(op,SYMBOLS.get(op,op)))+' '+right
  return left

def latex(expr):
 return s.latex(expr,mul_symbol='dot',ln_notation=True).replace(r'\frac',r'\dfrac')

def math(expr):return '$'+latex(expr)+'$'

def format_text(text,force=False):
 if not text:return text
 if '$' not in text:
  for raw,rendered in {'(f∘g)(x)':r'$(f\circ g)(x)$','f(g(x))':r'$f(g(x))$','∫1/x dx':r'$\int\dfrac{1}{x}\,dx$', 'ln|x|':r'$\ln|x|$'}.items():text=text.replace(raw,rendered)
 # Text emitted by the trusted engines, including their Unicode powers.
 text=text.replace('f⁻¹','finv').replace('g⁻¹','ginv').replace('⁻¹','^(-1)').replace('²','^2').replace('³','^3').replace('−','-')
 text=re.sub(r'([fFgP]\()([\d,]+)(\))',lambda m:m[1]+m[2].replace(',',', ')+m[3],text)
 pieces=re.split(r'(\$\$[\s\S]*?\$\$|\$[^$]*\$|`[^`]*`|https?://\S+)',text)
 for part in range(0,len(pieces),2):
  source=pieces[part];tokens=list(TOKEN.finditer(source));out=[];cursor=0;i=0
  while i<len(tokens):
   parser=Parser(tokens,i)
   try:value=parser.expr()
   except ValueError:i+=1;continue
   end=parser.i;raw=source[tokens[i].start():tokens[end-1].end()]
   # Do not turn a plain word, a Markdown list dash, or prose into math.
   marked=force or bool(re.search(r'[=<>≠≤≥≈→/^*×+\-∞μσΣ∩∪(]',raw)) or 'sqrt' in raw
   if marked:
    gap=source[cursor:tokens[i].start()]
    if not gap and out and out[-1].endswith('$'):gap=' '
    out.extend([gap,'$'+value+'$']);cursor=tokens[end-1].end()
   i=max(end,i+1)
  out.append(source[cursor:]);pieces[part]=''.join(out)
 return ''.join(pieces)

# Mathematical notation used in the original Statistics slides. Formulas for
# computationally equivalent forms keep population/sample distinctions explicit.
STAT_FORMULAS={
 'media':r'\bar{x}=\dfrac{\sum_{i=1}^{n}x_i}{n}',
 'media_ponderada':r'\bar{x}=\dfrac{\sum_i x_i f_i}{\sum_i f_i}',
 'valor_ausente':r'x_{\mathrm{ausente}}=n\bar{x}-\sum x_{\mathrm{conhecidos}}',
 'amplitude':r'R=x_{\max}-x_{\min}',
 'variancia_populacional':r'\sigma^2=\dfrac{\sum_{i=1}^{N}(x_i-\mu)^2}{N}',
 'variancia_amostral':r's^2=\dfrac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}',
 'desvio_padrao':r'\sigma=\sqrt{\dfrac{\sum_{i=1}^{N}(x_i-\mu)^2}{N}}',
 'uniao':r'P(A\cup B)=P(A)+P(B)-P(A\cap B)',
 'complemento':r"P(A^{c})=1-P(A)",
 'condicional':r'P(A\mid B)=\dfrac{P(A\cap B)}{P(B)},\quad P(B)>0',
 'arranjo':r'A_{n,k}=\dfrac{n!}{(n-k)!}',
 'combinacao':r'C_{n,k}=\dfrac{n!}{k!(n-k)!}',
 'permutacao':r'P_n=n!',
 'sem_reposicao':r'P(A\cap V)=\dfrac{n_A}{N}\cdot\dfrac{n_V}{N-1}',
 'correlacao':r'r=\dfrac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{(n-1)S_xS_y}',
 'interpretacao_correlacao':r'r=\dfrac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{(n-1)S_xS_y}',
 'robustez':r'\bar{x}=\dfrac{\sum_i x_i}{n}',
}

CALC_FORMULAS={
 'composicao':r'(f\circ g)(x)=f(g(x))','composicao_valor':r'(f\circ g)(x)=f(g(x))',
 'definicao':r"f'(x)=\lim_{h\to 0}\dfrac{f(x+h)-f(x)}{h}",
 'potencia':r"\dfrac{d}{dx}(kx^p)=kpx^{p-1}",
 'produto':r"(uv)'=u'v+uv'",'quociente':r"\left(\dfrac{u}{v}\right)'=\dfrac{u'v-uv'}{v^2}",
 'cadeia':r"\dfrac{d}{dx}F(u(x))=F'(u(x))u'(x)",
 'trigonometrica':r"(\sin x)'=\cos x;\quad(\cos x)'=-\sin x;\quad(\tan x)'=\sec^2x",
 'exponencial':r"(e^x)'=e^x",'logaritmica':r"(\ln x)'=\dfrac{1}{x}",
 'hiperbolica':r"(\sinh x)'=\cosh x;\quad(\cosh x)'=\sinh x",
 'implicita':r"\dfrac{d}{dx}(y^2)=2y\dfrac{dy}{dx}",
 'tangente':r"y-f(p)=f'(p)(x-p)", 'taxa':r"\mathrm{taxa\ instant\hat{a}nea}=f'(p)",
 'relacionadas':r'A=l^2;\quad\dfrac{dA}{dt}=2l\dfrac{dl}{dt}',
 'linearizacao':r"L(x)=f(p)+f'(p)(x-p)",'diferencial':r"dy=f'(x)\,dx",
 'crescimento':r"P'(t)=kP(t),\quad P(t)=P_0e^{kt}",
 'laterais':r'\lim_{x\to p^-}f(x)=\lim_{x\to p^+}f(x)=f(p)',
 'confronto':r'-1\le\sin(u)\le 1',
 'racionalizacao':r'(\sqrt{u}-a)(\sqrt{u}+a)=u-a^2',
}

def expression(text):
 normalized=text.replace('−','-').replace('²','^2').replace('³','^3')
 tokens=list(TOKEN.finditer(normalized));parser=Parser(tokens,0)
 try:
  value=parser.expr()
  if parser.i==len(tokens):return '$'+value+'$'
 except ValueError:pass
 return format_text(text)

def question_text(q):
 """Construct limits/integrals from their verified structured parameters."""
 spec=q.get('spec',{});motor=spec.get('motor');t=spec.get('topico')
 if motor=='integral':
  from app.practice.integral_engine import elaborar,X
  _,_,expr,limits=elaborar(spec)
  if t=='valor_multivariavel':return None
  integral=s.Integral(expr,*limits) if limits else s.Integral(expr,X)
  return 'Calcule '+math(integral)+(' no intervalo $x>0$.' if spec['tipo_funcao']=='RACIONAL' and not limits else '.')
 if motor!='calculo':return None
 from app.practice.calculo_engine import X
 x=X;a,b,n,c=map(s.Integer,spec['parametros']);tipo=spec['tipo_funcao']
 if t=='racionalizacao':p=a*a-b;expr=(s.sqrt(x+b)-a)/(x-p)
 elif t in {'fatoracao','fatoracao_limite'}:
  rest={2:b*(x+a),3:b*x+c,4:b*(x*x+a*x+a*a),5:b*(x-a)}[int(n)]
  expr=s.Mul(s.expand((x-a)*rest),s.Pow(x-a,-1,evaluate=False),evaluate=False);p=a
  if t=='fatoracao':return 'Simplifique '+math(expr)+', indicando a restrição do domínio.'
 elif t=='substituicao':
  p=c;expr=a*x*x+b*x+c if tipo=='POLINOMIAL' else (a*x+b)/(x*x+c) if tipo=='RACIONAL' else s.sqrt(x+b)
 elif t=='infinito':p=s.oo;expr=(a*x*x+b)/(c*x*x+1)
 elif t=='infinito_ponto':p=a;expr=b/(x-a)**2
 elif t=='confronto':p=0;expr=a*x*x*s.sin(b/x)
 else:return None
 return 'Calcule '+math(s.Limit(expr,x,p,dir='+-' if p!=s.oo else '-'))+'.'

def present(q):
 """Return a view; the original checked question and fingerprint stay intact."""
 result=copy.deepcopy(q)
 for key in ['enunciado','formula','substituicao','resolucao','dica']:
  if key in result:result[key]=format_text(result[key])
 for key in ['calculos','erros_comuns']:
  if key in result:result[key]=[format_text(t) for t in result[key]]
 if 'alternativas' in result:
  result['alternativas']={k:expression(v) for k,v in result['alternativas'].items()}
 if q.get('spec'):
  enunciado=question_text(q)
  if enunciado:result['enunciado']=enunciado
  family=q['spec'].get('familia')
  if family in STAT_FORMULAS:result['formula']='$'+STAT_FORMULAS[family]+'$'
  t=q['spec'].get('topico')
  if q['spec'].get('motor')=='calculo' and t in CALC_FORMULAS:result['formula']='$'+CALC_FORMULAS[t]+'$'
  if family=='iqr':result['formula']=r'$h=(n-1)q$ (índice iniciado em zero, interpolação linear); $IQR=Q_3-Q_1$.'
  if q['spec'].get('motor')=='integral' and t in {'primitiva','integral_direta'}:result['formula']=r'$\int x^p\,dx=\dfrac{x^{p+1}}{p+1}+C$, para $p\ne-1$; linearidade e tabela de integrais.'
  if q['spec'].get('motor')=='integral' and t=='integral_definida':result['formula']=r'$\int_a^b f(x)\,dx=F(b)-F(a)$, para $f$ contínua em $[a,b]$.'
  if result.get('calculos'):result['resolucao']='\n\n'.join(f'{i}. {step}' for i,step in enumerate(result['calculos'],1))
 elif q.get('conceito')=='Desvio-padrão':result['formula']='$'+STAT_FORMULAS['desvio_padrao']+'$'
 elif q.get('conceito')=='Probabilidade condicional':result['formula']='$'+STAT_FORMULAS['condicional']+'$'
 elif q.get('conceito')=='Covariância e associação linear':result['formula']=r'$\operatorname{cov}(X,Y)=\dfrac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{n-1}$, para amostra.'
 return result
