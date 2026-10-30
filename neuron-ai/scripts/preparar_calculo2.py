"""Gera apoios autorais e corpus; execute com Python que contenha reportlab e pymupdf."""
from pathlib import Path
import hashlib
import json
import shutil

RAIZ=Path(__file__).resolve().parents[1]
PASTA=RAIZ/'materiais_academicos/periodo_03/calculo_para_computacao_2'
ASSUNTOS=[('primitivas','1ª unidade · Primitivas'),('integrais_indefinidas','1ª unidade · Integrais indefinidas'),
 ('integrais_definidas','1ª unidade · Integrais definidas'),('integrais_duplas_retangulares','2ª unidade · Integrais duplas em retângulos'),
 ('integrais_duplas_iteradas','2ª unidade · Integrais duplas iteradas'),('integrais_triplas_retangulares','2ª unidade · Integrais triplas em caixas'),
 ('integrais_triplas_iteradas','2ª unidade · Integrais triplas iteradas'),('base_multivariavel','Complemento opcional · Funções de várias variáveis')]

GUIA=[
 ('Primitivas: o caminho de volta da derivada',[
 'Cálculo para Computação II | 3º período | 1ª unidade',
 'Apoio autoral NEURON gerado com IA. Organização conforme o escopo informado pelo aluno; não é uma apostila ou ementa oficial do professor.',
 'Uma primitiva F de f satisfaz F′(x)=f(x). A integral indefinida reúne todas as primitivas em um intervalo: ∫ f(x) dx = F(x)+C.',
 'Exemplo resolvido: ∫ (6x²+4x-3) dx. Pela linearidade, integre cada parcela: 6x³/3 + 4x²/2 - 3x + C = 2x³+2x²-3x+C. Derivando o resultado, recuperamos 6x²+4x-3.',
 'Por que C? A derivada de 2x³+2x²-3x+7 é a mesma da expressão com +12. A constante registra essa família.',
 'Treino: a) ∫ 5 dx; b) ∫ (4x³-2x+1) dx; c) ∫ (3x²+2) dx.',
 'Respostas: a) 5x+C; b) x⁴-x²+x+C; c) x³+2x+C.',
 'Método: identifique a variável; simplifique; escolha a fórmula na tabela; integre; acrescente C; derive para conferir.']),
 ('Integrais indefinidas: cálculo direto',[
 '1ª unidade | Uma variável | Consulte a Tabela de Integrais - apoio NEURON.',
 'Potências: ∫ x^p dx = x^(p+1)/(p+1)+C para p ≠ -1, em intervalos do domínio real da potência. Aumente o expoente e divida pelo novo expoente.',
 'Exemplo com radical: ∫ (3√x+2) dx = ∫ (3x^(1/2)+2) dx = 2x^(3/2)+2x+C, para x ≥ 0.',
 'Exceção importante: ∫ 1/x dx = ln|x|+C, em um intervalo que não cruza zero. Não use a fórmula da potência com p=-1.',
 'Trigonométricas em radianos: ∫ sen x dx = -cos x+C e ∫ cos x dx = sen x+C. Exemplo: ∫ (2sen x+3cos x) dx = -2cos x+3sen x+C.',
 'Exponenciais: ∫ e^x dx=e^x+C. Para a constante a ≠ 0, ∫ e^(ax+b) dx=e^(ax+b)/a+C. A divisão por a compensa a regra da cadeia.',
 'Treino: a) ∫ (2x³+4/x) dx em x>0; b) ∫ (4cos x-3sen x) dx; c) ∫ 2e^x dx; d) ∫ 5/√x dx em x>0.',
 'Respostas: a) x⁴/2+4ln x+C; b) 4sen x+3cos x+C; c) 2e^x+C; d) 10√x+C.',
 'Substituição e partes aparecem na tabela como consulta adicional. Sua inclusão na cobrança não foi confirmada; o treino padrão prioriza integração direta.']),
 ('Integrais definidas: aplique os limites',[
 '1ª unidade | Apenas uma variável.',
 'Se f é contínua em [a,b] e F′=f, então ∫ de a a b f(x) dx = F(b)-F(a). Primeiro encontre uma primitiva; depois aplique os limites.',
 'Exemplo: ∫ de 0 a 2 (3x²-2x) dx. Uma primitiva é F(x)=x³-x². F(2)=8-4=4; F(0)=0. Resultado: 4-0=4.',
 'A constante C cancela: [F(b)+C]-[F(a)+C]=F(b)-F(a). O resultado de uma integral definida é um número, e não uma família com +C.',
 'A integral é uma acumulação com sinal. Só representa diretamente área geométrica quando o integrando é não negativo. Para área com troca de sinal, separe os intervalos e integre o valor absoluto.',
 'Exemplo: ∫ de -1 a 1 x dx = [x²/2] de -1 a 1 = 0. A área geométrica entre a reta e o eixo nesse intervalo é 1.',
 'Treino: a) ∫ de 0 a 1 (4x+2) dx; b) ∫ de 1 a 2 1/x dx; c) ∫ de 0 a π sen x dx; d) ∫ de 0 a 1 e^x dx.',
 'Respostas: a) 4; b) ln 2; c) 2; d) e-1.',
 'Erro comum: substituir os limites antes de encontrar a primitiva ou calcular F(a)-F(b). Confira a ordem.']),
 ('Integrais duplas em retângulos',[
 '2ª unidade proposta | Cálculo direto em coordenadas cartesianas.',
 'Uma função f(x,y) recebe um par de valores. Ao integrar em y, trate x como constante. Em ∫ de 0 a 1 ∫ de 0 a 2 f(x,y) dy dx, faça primeiro y, depois x.',
 'Para f contínua em um retângulo, Fubini permite calcular a integral dupla por integrais iteradas. O retângulo é indicado pelos dois pares de limites constantes.',
 'Exemplo: ∫ de 0 a 1 ∫ de 0 a 2 (x+2y) dy dx.',
 'Etapa interna: ∫ (x+2y) dy = xy+y². Aplicando y=0 e y=2: 2x+4.',
 'Etapa externa: ∫ de 0 a 1 (2x+4) dx = [x²+4x] de 0 a 1 = 5.',
 'Não derive x nem o elimine: em relação a y ele é uma constante, por isso ∫ x dy = xy.',
 'Treino: a) ∫ de 0 a 1 ∫ de 0 a 2 (x+y) dy dx; b) ∫ de 0 a 1 ∫ de 1 a 2 xy² dy dx.',
 'Respostas: a) 3; b) 7/6. Fonte complementar: guia de várias variáveis recebido, páginas físicas 55-56.']),
 ('Integrais duplas com limites variáveis',[
 '2ª unidade proposta | Os limites já são fornecidos no enunciado.',
 'Exemplo: ∫ de 0 a 1 ∫ de 0 a x (x+y) dy dx. A região satisfaz 0 ≤ x ≤ 1 e 0 ≤ y ≤ x.',
 'Integre em y mantendo x fixo: xy+y²/2. Avalie entre y=0 e y=x: x²+x²/2 = 3x²/2.',
 'Integre em x: ∫ de 0 a 1 3x²/2 dx = [x³/2] de 0 a 1 = 1/2.',
 'Um limite que contém x só é substituído na etapa correspondente à variável integrada. Ao terminar a integral interna em y, y deve desaparecer.',
 'Treino: a) ∫ de 0 a 2 ∫ de 0 a x (2x+y) dy dx; b) ∫ de 0 a 1 ∫ de 0 a x xy dy dx.',
 'Respostas: a) 20/3; b) 1/8.',
 'O treino padrão não exige mudança de coordenadas, Jacobiano nem reconstrução de regiões. Esses temas existem no complemento amplo, mas não foram informados como cobrança.']),
 ('Integrais triplas em caixas',[
 '2ª unidade proposta | Três integrações simples sucessivas.',
 'Exemplo: ∫ de 0 a 1 ∫ de 0 a 2 ∫ de 0 a 1 (x+y+z) dz dy dx.',
 'Em z: xz+yz+z²/2. Entre 0 e 1 resulta x+y+1/2.',
 'Em y: xy+y²/2+y/2. Entre 0 e 2 resulta 2x+3.',
 'Em x: x²+3x. Entre 0 e 1 resulta 4.',
 'Em cada etapa, apenas a variável do diferencial é integrada. As outras são constantes nessa etapa. Não acrescente +C em integrais internas definidas.',
 'Treino: a) ∫ de 0 a 1 ∫ de 0 a 1 ∫ de 0 a 1 xyz dz dy dx; b) a mesma caixa com integrando 2x+y+z.',
 'Respostas: a) 1/8; b) 2. Com integrando 1, o resultado é o volume da região.']),
 ('Integrais triplas com limites variáveis',[
 '2ª unidade proposta | Leia os diferenciais de dentro para fora.',
 'Exemplo: ∫ de 0 a 1 ∫ de 0 a x ∫ de 0 a x+y 1 dz dy dx.',
 'Em z, uma primitiva de 1 é z. Aplicando z=x+y e z=0 resulta x+y.',
 'Em y, uma primitiva de x+y é xy+y²/2. Entre 0 e x resulta 3x²/2.',
 'Em x, ∫ de 0 a 1 3x²/2 dx = 1/2. Esse é o volume do sólido descrito pelos limites.',
 'Treino: a) ∫ de 0 a 1 ∫ de 0 a x ∫ de 0 a y 1 dz dy dx; b) ∫ de 0 a 1 ∫ de 0 a x ∫ de 0 a x+y (x+y+z) dz dy dx.',
 'Respostas: a) 1/6; b) 7/8.',
 'Trilha opcional: antes de estudar funções de várias variáveis em profundidade, revise avaliação f(a,b), domínio e a ideia de manter variáveis fixas. No PDF complementar recebido, páginas físicas 13-17 dão essa base. Gradiente, otimização e Lagrange ficam fora dos simulados padrão.',
 'Referências: escopo informado pelo aluno; complemento de IA recebido (capítulos 10-11 para consulta); prova transcrita de Cálculo I apenas para observar o formato. Este apoio não atribui conteúdo novo ao professor.'])]

TABELA=[('Tabela de Integrais - apoio NEURON',[
 'Consulta autoral de estudo | Cálculo II | Não é uma tabela emitida pelo professor.',
 'Em cada fórmula indefinida, C é uma constante. As fórmulas valem em intervalos em que integrando e primitiva estão definidos; trigonometria em radianos.',
 '∫ k dx = kx+C;     ∫ [af(x)+bg(x)] dx = a∫f(x)dx+b∫g(x)dx.',
 '∫ x^p dx = x^(p+1)/(p+1)+C, p ≠ -1, no domínio real da potência.',
 '∫ 1/x dx = ln|x|+C, x ≠ 0, em cada intervalo sem zero.',
 '∫ √x dx = (2/3)x^(3/2)+C, x ≥ 0.',
 '∫ 1/√x dx = 2√x+C, x > 0.',
 '∫ e^x dx = e^x+C;     ∫ e^(ax+b) dx = e^(ax+b)/a+C, a ≠ 0.',
 '∫ q^x dx = q^x/ln(q)+C, q > 0 e q ≠ 1.',
 '∫ sen x dx = -cos x+C;     ∫ cos x dx = sen x+C.',
 '∫ sec²x dx = tg x+C;     ∫ cossec²x dx = -cotg x+C.',
 '∫ sec x tg x dx = sec x+C;     ∫ cossec x cotg x dx = -cossec x+C.',
 '∫ 1/(1+x²) dx = arctg x+C.',
 '∫ 1/√(1-x²) dx = arcsen x+C, |x| < 1.',
 'Para funções trigonométricas com denominadores, trabalhe em um intervalo onde esses denominadores não se anulam.']),
 ('Regras para aplicar a tabela',[
 'Integral definida: ∫ de a a b f(x) dx = F(b)-F(a), com f contínua em [a,b] e F′=f. Não acrescente +C ao resultado numérico.',
 '∫ de a a a f(x) dx=0; inverter os limites troca o sinal. Somar intervalos adjacentes preserva a integral.',
 'Composição linear: ∫ f(ax+b) dx = F(ax+b)/a+C, a ≠ 0, quando F′=f. Exemplo: ∫ cos(3x+1) dx = sen(3x+1)/3+C.',
 'Consulta adicional, cobrança não confirmada: substituição u=g(x), du=g′(x)dx; ∫ f(g(x))g′(x)dx = F(g(x))+C. Na definida, transforme também os limites ou volte a x antes de aplicá-los.',
 'Consulta adicional, cobrança não confirmada: integração por partes ∫u dv = uv-∫v du. Não confunda com a regra do produto: ∫fg não é (∫f)(∫g).',
 'Duplas: ∫ de a a b ∫ de c a d f(x,y) dy dx. Primeiro integre em y, mantendo x constante; aplique c e d; depois integre em x e aplique a e b.',
 'Triplas: em ∫∫∫ f(x,y,z) dz dy dx, a ordem é z, depois y e depois x. Limites variáveis também são aplicados ao fim de cada etapa.',
 'Fubini no caso usado: integrandos contínuos nas regiões limitadas dos exercícios permitem a integração iterada. Não troque a ordem sem ajustar os limites.',
 'Conferência: derive a primitiva; nas definidas verifique F(superior)-F(inferior); nas múltiplas confira se a variável interna desapareceu depois de aplicar seus limites.',
 'Complemento opcional: funções de várias variáveis são apoio de base. Gradiente, Lagrange e mudanças de coordenadas não integram o simulado padrão.'])]

PROVA=[('Simulado aberto - 1ª unidade',[
 'Cálculo para Computação II | 3º período | Nome: ______________________',
 'Atividade autoral de estudo. A disciplina não tem prova oficial. Formato inspirado na amostra de Cálculo I: comandos diretos, subitens, consulta a fórmulas e resolução no papel. Tempo sugerido: 180 minutos. Total proposto: 8,0 pontos.',
 'Consulta permitida: Tabela de Integrais - apoio NEURON. Mostre a regra, os cálculos e a resposta. Apenas integrais de uma variável nesta unidade.',
 '1) Calcule as integrais indefinidas (1,5 ponto; 0,5 cada):\na) ∫ (6x²-4x+3) dx.\nb) ∫ 5√x dx.\nc) ∫ (2/x) dx, em x > 0.',
 '2) Calcule (1,5 ponto; 0,5 cada):\na) ∫ 3e^x dx.\nb) ∫ (2cos x-4sen x) dx.\nc) ∫ (x³+2x²-x+1) dx.',
 '3) Determine F, sabendo que F′(x)=4x e F(1)=5 (0,5 ponto).',
 '4) Calcule as integrais definidas (1,5 ponto; 0,5 cada):\na) ∫ de 0 a 2 (3x²+1) dx.\nb) ∫ de 1 a 4 (1/√x) dx.\nc) ∫ de 1 a 2 (1/x) dx.',
 '5) Calcule (1,0 ponto; 0,5 cada):\na) ∫ de 0 a π sen x dx.\nb) ∫ de 0 a 1 e^x dx.',
 '6) Calcule ∫ de -1 a 1 x dx e a área geométrica entre y=x e o eixo x nesse intervalo (0,5 ponto).',
 '7) Calcule apenas duas alternativas, identificando as escolhidas (1,0 ponto; 0,5 cada):\na) ∫ x⁴ dx.  b) ∫ x^(-2) dx em x>0.  c) ∫ 7 dx.  d) ∫ cos x dx.',
 '8) Confira por derivação se F(x)=x³+2x é uma primitiva de f(x)=3x²+2 e escreva a família de primitivas (0,5 ponto).',
 'Registre as resoluções em folhas separadas. O gabarito comentado começa na terceira página.']),
 ('Simulado aberto - 2ª unidade',[
 'Atividade autoral | Consulta à tabela | Tempo sugerido: 180 minutos | Total: 8,0 pontos.',
 'A divisão desta unidade é uma proposta de organização: integrais duplas e triplas por cálculo direto em cartesianas, com os limites já fornecidos. Mostre cada integração e cada aplicação dos limites.',
 '1) Calcule (1,5 ponto): ∫ de 0 a 1 ∫ de 0 a 2 (x+2y) dy dx.',
 '2) Calcule (1,0 ponto): ∫ de 0 a 1 ∫ de 1 a 2 xy² dy dx.',
 '3) Calcule (1,0 ponto): ∫ de 0 a 1 ∫ de 0 a x (x+y) dy dx.',
 '4) Calcule (0,5 ponto): ∫ de 0 a 1 ∫ de 0 a 1 3 dx dy. Atenção à ordem indicada.',
 '5) Calcule (1,5 ponto): ∫ de 0 a 1 ∫ de 0 a 2 ∫ de 0 a 1 (x+y+z) dz dy dx.',
 '6) Calcule (1,0 ponto): ∫ de 0 a 1 ∫ de 0 a 1 ∫ de 0 a 1 xyz dz dy dx.',
 '7) Calcule (1,0 ponto): ∫ de 0 a 1 ∫ de 0 a x ∫ de 0 a x+y 1 dz dy dx.',
 '8) Calcule (0,5 ponto): ∫ de 0 a 1 ∫ de 0 a x ∫ de 0 a y 1 dz dy dx.',
 'Critério sugerido: metade da pontuação pelo uso correto das primitivas, um quarto pela aplicação dos limites e um quarto pelo resultado. Sem questões de gradiente, otimização, Lagrange ou mudanças de coordenadas.']),
 ('Gabarito comentado - 1ª unidade',[
 'Resoluções autorais; não há gabarito oficial do professor para este simulado.',
 '1a) Potência e linearidade: 6x³/3-4x²/2+3x+C = 2x³-2x²+3x+C.\n1b) √x=x^(1/2): 5x^(3/2)/(3/2)+C = (10/3)x^(3/2)+C.\n1c) Pela exceção da potência: 2ln x+C, no intervalo x>0.',
 '2a) 3e^x+C.\n2b) 2sen x+4cos x+C. Note que ∫(-sen x) dx = cos x+C.\n2c) x⁴/4+(2/3)x³-x²/2+x+C.',
 '3) Integre F′=4x: F=2x²+C. Como F(1)=5, 2+C=5 e C=3. Logo F(x)=2x²+3.',
 '4a) F=x³+x. F(2)-F(0)=10.\n4b) F=2√x. F(4)-F(1)=4-2=2.\n4c) F=ln x em [1,2]. ln 2-ln 1=ln 2.',
 '5a) F=-cos x. -cos π-(-cos 0)=1-(-1)=2.\n5b) F=e^x. e^1-e^0=e-1.',
 '6) Integral: [x²/2] de -1 a 1 = 0. Área: -∫ de -1 a 0 x dx + ∫ de 0 a 1 x dx = 1/2+1/2=1.',
 '7a) x⁵/5+C.\n7b) -1/x+C, no intervalo x>0.\n7c) 7x+C.\n7d) sen x+C. Corrija somente as duas alternativas escolhidas.',
 '8) F′=3x²+2=f. Portanto F é primitiva e a família é x³+2x+C.',
 'Pontuação total: 1,5+1,5+0,5+1,5+1,0+0,5+1,0+0,5=8,0.']),
 ('Gabarito comentado - 2ª unidade',[
 '1) Em y: [xy+y²] de 0 a 2 = 2x+4. Em x: [x²+4x] de 0 a 1 = 5.',
 '2) Em y: [xy³/3] de 1 a 2 = 7x/3. Em x: [7x²/6] de 0 a 1 = 7/6.',
 '3) Em y: [xy+y²/2] de 0 a x = 3x²/2. Em x: [x³/2] de 0 a 1 = 1/2.',
 '4) Em x: [3x] de 0 a 1 = 3. Em y: [3y] de 0 a 1 = 3.',
 '5) Em z: [xz+yz+z²/2] de 0 a 1 = x+y+1/2. Em y: [xy+y²/2+y/2] de 0 a 2 = 2x+3. Em x: [x²+3x] de 0 a 1 = 4.',
 '6) Em z: [xyz²/2] de 0 a 1 = xy/2. Em y: [xy²/4] de 0 a 1 = x/4. Em x: [x²/8] de 0 a 1 = 1/8.',
 '7) Em z: [z] de 0 a x+y = x+y. Em y: [xy+y²/2] de 0 a x = 3x²/2. Em x: [x³/2] de 0 a 1 = 1/2.',
 '8) Em z: [z] de 0 a y = y. Em y: [y²/2] de 0 a x = x²/2. Em x: [x³/6] de 0 a 1 = 1/6.',
 'Pontuação total: 1,5+1,0+1,0+0,5+1,5+1,0+1,0+0,5=8,0.',
 'Para uma final ou segunda chamada de estudo, selecione questões das duas unidades; mantenha funções de várias variáveis como complemento opcional. Na plataforma, os simulados usam cinco alternativas de conferência; neste PDF, o formato é aberto, como na amostra do professor.'])]

def gerar_pdfs():
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import simpleSplit
    pdfmetrics.registerFont(TTFont('Cambria',r'C:\Windows\Fonts\cambria.ttc',subfontIndex=0))
    PASTA.mkdir(parents=True,exist_ok=True)
    for nome,paginas in [('Guia de Integrais - NEURON.pdf',GUIA),('Tabela de Integrais - apoio NEURON.pdf',TABELA),('Simulados abertos de Integrais - NEURON.pdf',PROVA)]:
        doc=canvas.Canvas(str(PASTA/nome),pagesize=(595,842));doc.setTitle(nome[:-4]);doc.setAuthor('NEURON - apoio autoral com IA')
        for num,(titulo,blocos) in enumerate(paginas,1):
            doc.setFillColorRGB(.08,.21,.28);doc.rect(0,765,595,77,fill=1,stroke=0)
            doc.setFillColorRGB(1,1,1);doc.setFont('Cambria',17);doc.drawString(42,795,titulo)
            doc.setFillColorRGB(.12,.15,.19);y=737
            for bloco in blocos:
                for linha in bloco.split('\n'):
                    for pedaco in simpleSplit(linha,'Cambria',11,511):
                        doc.setFont('Cambria',11);doc.drawString(42,y,pedaco);y-=15
                y-=12
            if y<60:raise ValueError(f'Página excedida: {nome} {num}: {y}')
            doc.setFont('Cambria',9);doc.setFillColorRGB(.35,.4,.45);doc.drawString(42,30,'NEURON | Apoio de estudo autoral | Cálculo para Computação II');doc.drawRightString(553,30,f'{num}/{len(paginas)}');doc.showPage()
        doc.save()

def corpus():
    import pymupdf
    arquivos=[];paginas=[];chunks=[]
    for pdf in sorted(PASTA.glob('*.pdf')):
        digest=hashlib.sha256(pdf.read_bytes()).hexdigest();complemento=pdf.name.startswith('funçoes');simulado=pdf.name.startswith('Simulados');tabela=pdf.name.startswith('Tabela')
        doc=pymupdf.open(pdf);arquivos.append(dict(arquivo=pdf.name,pdf=pdf.relative_to(RAIZ).as_posix(),pdf_sha256=digest,titulo=pdf.stem,tipo='RESUMO',paginas=len(doc)))
        for i,page in enumerate(doc,1):
            if complemento:slugs=['base_multivariavel']
            elif simulado:slugs=[a[0] for a in ASSUNTOS[:3]] if i in [1,3] else [a[0] for a in ASSUNTOS[3:7]]
            elif tabela:slugs=[a[0] for a in ASSUNTOS[:7]]
            else:slugs=[ASSUNTOS[i-1][0]]
            text=page.get_text().replace('\x00','').strip()
            # Também preserva o texto autorado, sem perda de símbolos na extração.
            if not complemento:
                registro=(TABELA if tabela else PROVA if simulado else GUIA)[i-1]
                text=registro[0]+'\n\n'+'\n\n'.join(registro[1])
            for slug in slugs:
                idx=[a[0] for a in ASSUNTOS].index(slug);meta=dict(periodo='03',disciplina='calculo_para_computacao_2',assunto=slug,unidade=0 if complemento else 1 if idx<3 else 2,
                    arquivo=pdf.name,pagina=i,tipo_arquivo='pdf',tipo_extracao='textual',tipo_material='RESUMO',pdf_sha256=digest,titulo_material=pdf.stem,
                    complementar=complemento,autoria='IA fornecida pelo aluno' if complemento else 'Apoio autoral NEURON com IA',prova_oficial=False)
                paginas.append(dict(conteudo=text,metadata=meta.copy()))
                for j,start in enumerate(range(0,len(text),850)):
                    identity=f'{digest}|{i}|{slug}|{j}';cid=hashlib.sha256(identity.encode()).hexdigest()[:24]
                    chunks.append(dict(chunk_id=cid,conteudo=text[start:start+1000],metadata=dict(meta,chunk_index=j,chunk_id=cid)))
    data=dict(disciplina='calculo_para_computacao_2',periodo='03',arquivos=arquivos,paginas=paginas,chunks=chunks,total_chunks=len(chunks),total_paginas=sum(a['paginas'] for a in arquivos),
        prova=dict(oficial=False,formato_referencia='Prova transcrita de Cálculo I; comandos diretos e questões abertas; não usar como fonte de conteúdo de integrais.'),
        escopo='Unidade 1 apenas integrais simples. Unidade 2 proposta: integrais duplas e triplas diretas em cartesianas. Complemento opcional fora dos simulados padrão.')
    (PASTA/'corpus.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return data

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--pdfs',action='store_true');parser.add_argument('--corpus',action='store_true');args=parser.parse_args()
    if args.pdfs:gerar_pdfs()
    if args.corpus:
        origem=Path(r'C:\Users\Pichau\Downloads\Calculo para Computação I\funçoes cde duas variaveis.pdf')
        shutil.copy2(origem,PASTA/origem.name)
        dados=corpus();print(json.dumps({k:dados[k] for k in ['total_paginas','total_chunks']}))
