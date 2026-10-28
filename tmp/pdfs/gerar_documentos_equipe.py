from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
TMP = ROOT / 'tmp' / 'pdfs'
NAVY = colors.HexColor('#12243D')
TEAL = colors.HexColor('#087E8B')
GRAY = colors.HexColor('#526174')
PALE = colors.HexColor('#EDF4F7')
LINE = colors.HexColor('#D9E2E9')
FONT = Path('C:/Windows/Fonts')
for name, filename in [('Body','segoeui.ttf'),('Bold','segoeuib.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')
styles = getSampleStyleSheet()
for name,size,leading,color in [('BodyText',10,15, NAVY),('Title',27,32,NAVY),('Heading1',18,23,NAVY),('Heading2',12,17,TEAL)]:
    styles[name].fontName='Body' if name=='BodyText' else 'Bold'
    styles[name].fontSize=size
    styles[name].leading=leading
    styles[name].textColor=color
    styles[name].spaceAfter=9
styles.add(ParagraphStyle(name='Small',fontName='Body',fontSize=8.2,leading=12,textColor=GRAY,spaceAfter=6))
styles.add(ParagraphStyle(name='Cell',fontName='Body',fontSize=8.7,leading=12,textColor=NAVY))
styles.add(ParagraphStyle(name='CellHead',fontName='Bold',fontSize=8.7,leading=12,textColor=colors.white))
styles.add(ParagraphStyle(name='Kicker',fontName='Bold',fontSize=9,leading=13,textColor=TEAL,spaceAfter=9))

def p(text, style='BodyText'):
    return Paragraph(text, styles[style])

def h(text):
    return p(text,'Heading2')

def bullets(items):
    return [p('• '+x) for x in items]

def table(headers, rows, widths):
    data=[[p(escape(x),'CellHead') for x in headers]]
    data += [[p(x,'Cell') for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[PALE,colors.white]),
        ('LINEBELOW',(0,-1),(-1,-1),0.6,LINE)
    ]))
    return t

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*args,**kwargs):
        canvas.Canvas.__init__(self,*args,**kwargs)
        self.states=[]
    def showPage(self):
        self.states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        count=len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            self.setStrokeColor(LINE)
            self.line(44,47,551,47)
            self.setFont('Body',8)
            self.setFillColor(GRAY)
            self.drawString(44,32,'NEURON  |  Equipe do projeto  |  28/10/2026')
            self.drawRightString(551,32,f'{self._pageNumber} / {count}')
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

def header(c,doc):
    c.setFillColor(NAVY)
    c.rect(0,816,595.28,26,fill=1,stroke=0)
    c.setFont('Bold',8)
    c.setFillColor(colors.white)
    c.drawString(44,825,'NEURON / MONITOR VIRTUAL')
    c.drawRightString(551,825,doc.title)

def build(name,title,story):
    doc=SimpleDocTemplate(str(OUT/name),pagesize=(595.28,841.89),rightMargin=44,leftMargin=44,topMargin=53,bottomMargin=65,title=title,author='Equipe NEURON',subject='Situação do projeto e planejamento do piloto')
    doc.build(story,onFirstPage=header,onLaterPages=header,canvasmaker=NumberedCanvas)
    return OUT/name

def page(kicker,title):
    return [p(kicker,'Kicker'),p(title,'Title'),Spacer(1,5)]

report=page('01 / VISÃO EXECUTIVA','Relatório de desenvolvimento')
report += [p('Situação atual, entregas e próximos passos','Heading1'),p('Data de referência: 28 de outubro de 2026. Documento preparado para comunicação e alinhamento da equipe.','Small'),
    p('O NEURON já possui um fluxo integrado de estudo: o estudante acessa uma disciplina, consulta materiais, conversa com o Monitor Virtual e pode reabrir o histórico. A integração e a continuidade das conversas foram validadas no ambiente local.'),
    table(['Testes registrados','Cenários com IA real','Base de materiais'],[['<b>165 aprovados</b><br/>34 backend · 117 IA · 14 interface','<b>16 de 16 aprovados</b><br/>Quatro cenários por disciplina','<b>955 trechos indexados</b><br/>Distribuídos em quatro disciplinas']],[169,169,169]),Spacer(1,16),
    h('O que esta entrega representa'),
    p('A base técnica permite demonstrar o Monitor Virtual com materiais de aula, referências e perguntas de continuação. Estrutura de Dados Avançada foi integrada ao catálogo, aos arquivos e ao serviço de IA.'),
    h('Distinção importante para a equipe'),
    p('As quatro disciplinas têm conteúdo na base da IA, mas o catálogo da interface conferido nesta etapa exibia apenas Estatística e Estrutura de Dados Avançada. A presença de conteúdo na IA não significa que a disciplina já esteja acessível no catálogo.'),
    h('Situação da entrega'),
    p('<b>Implementado e validado localmente.</b> Hospedagem pública, capacidade com vários acessos e validação com professores e alunos ainda precisam ser preparadas.'),
    p('Os números reproduzem evidências já registradas no projeto. Nenhuma nova execução de testes ou consulta paga ao modelo foi realizada para emitir este documento.','Small'),PageBreak()]

report += page('02 / ENTREGAS','O que já está implementado')
report += [table(['Frente','Entrega e efeito para o usuário'],[
    ['Interface e navegação','Interface React derivada do protótipo, com disciplinas, materiais, Monitor Virtual e histórico. Há adaptações para computador, tablet e celular documentadas.'],
    ['Integração dos serviços','O navegador usa o backend Spring Boot; o serviço Python executa a busca e a geração. As chaves do provedor ficam fora do navegador.'],
    ['Estrutura de Dados Avançada','Disciplina no 3º período, 14 assuntos e três PDFs: Aula 0, Aula 1 e Aula 2. Os 167 trechos existentes foram vinculados ao cadastro.'],
    ['Conversa com contexto','Até oito mensagens recentes da mesma conversa ajudam a interpretar “explique melhor”, “mais visual” e pedidos de novos exemplos.'],
    ['Referências e materiais','As respostas usam fontes recuperadas dos materiais. Há links para os arquivos e páginas citadas quando disponíveis.'],
    ['Histórico e acesso','Perguntas, respostas e fontes são persistidas. Acesso às conversas é restrito ao dono; os materiais respeitam os filtros atuais.'],
    ['Recursos didáticos','Tabelas e esquemas em texto. Exemplos novos são identificados como criações didáticas da IA, apoiadas nas fontes conceituais.'],
    ['Avaliação da plataforma','A documentação registra avaliação voluntária do estudante, com nota e comentário opcional, sem impedir o uso da plataforma.']
    ],[126,381]),Spacer(1,13),h('Correções relevantes'),
    p('A recuperação em Estrutura de Dados combina busca por significado e por termos para evitar perder definições úteis. O histórico passou a chegar à IA; também foi ajustada a preservação de esquemas e suas referências.'),PageBreak()]

report += page('03 / EVIDÊNCIAS','O que foi validado')
report += [table(['Camada','Testes','Principais verificações'],[
    ['Backend','34','Autenticação, isolamento de contas e contextos, catálogo, materiais e histórico.'],
    ['Serviço de IA','117','Busca, continuidade, mudança de tema, fontes, esquemas e validação dos formatos.'],
    ['Interface','14','Envio e falhas, histórico, tabelas, esquemas, materiais, avaliação e prática.'],
    ['Total','165','Aprovados nas execuções consolidadas da entrega.']],[100,55,352]),Spacer(1,14),
    h('Cenários com o modelo real'),
    p('Foram executados quatro cenários em cada disciplina: pergunta inicial, continuação didática ou visual, pedido de outro exemplo e pergunta independente sem cobertura nos materiais. O relatório final registra 16 aprovações e nenhuma falha.'),
    table(['Disciplina','Trechos na base','Cenários aprovados'],[
    ['Estrutura de Dados Avançada','167','4 de 4'],['Estatística','208','4 de 4'],['Design de Artefatos Digitais','363','4 de 4'],['Projeto de Ideação de Software','217','4 de 4']],[317,95,95]),Spacer(1,14),
    h('Integração e preservação dos dados'),
    p('Uma conta temporária confirmou a passagem do contexto pelo backend, a resposta visual de continuação e a reabertura das mensagens com fontes. A integração dos materiais de Estrutura de Dados foi repetida sem alterações; os 955 trechos das quatro disciplinas foram preservados.'),
    p('Esses resultados demonstram os cenários executados. A qualidade acadêmica de todas as respostas futuras ainda depende de avaliação contínua com os professores.','Small'),PageBreak()]

report += page('04 / CONTINUIDADE','Pendências e decisões da equipe')
report += [table(['Ordem','Próximo passo','Dependência / participação'],[
    ['1','Completar o catálogo com Design e Ideação.','Desenvolvimento e conferência do cadastro e dos vínculos com materiais.'],
    ['2','Preparar o piloto e revisar perguntas de referência.','Professores e alunos participantes; validação das fontes e da utilidade das respostas.'],
    ['3','Habilitar prática de Estrutura de Dados quando houver material elegível.','Listas ou provas autorizadas e cadastradas; slides não substituem avaliações.'],
    ['4','Preparar hospedagem e operação.','Definir ambiente, orçamento, acesso, backups, monitoramento e teste simultâneo.'],
    ['5','Melhorar a apresentação durante a geração.','Avaliar entrega progressiva do texto; hoje a resposta chega após a geração completa.']],[60,252,195]),Spacer(1,12),
    h('Limites atuais'),
    p('O contexto da IA usa uma janela recente, sem memória ilimitada de todas as conversas. Os recursos visuais são tabelas e esquemas textuais. A prática de Estrutura de Dados está desabilitada. Não há demonstração de carga ou de operação pública nesta entrega.'),
    h('Alinhamentos necessários'),
    p('A equipe deve definir responsáveis e datas, confirmar os materiais autorizados, escolher os participantes do piloto e aprovar o escopo da primeira versão. Este relatório não atribui compromissos individuais nem presume prazos.'),
    h('Fontes internas utilizadas'),
    p('Caminhos relativos à pasta NEURON. Registros consultados em 28/10/2026:','Small'),
    p('• output/pdf/NEURON_Relatorio_Desenvolvimento_Validacao_2026-10-28.md<br/>• docs/CHAT_CONVERSACIONAL_RAG.md<br/>• docs/BACKEND_ED_AVANCADA.md<br/>• docs/FRONTEND_E_HISTORICO.md<br/>• neuron-ai/saidas_testes/validacao_conversa_rag.json','Small')]

mvp=page('01 / DEFINIÇÃO DO PRODUTO','MVP do NEURON')
mvp += [p('Proposta de primeira versão para piloto','Heading1'),p('28 de outubro de 2026  |  Escopo sugerido para alinhamento da equipe','Small'),
    h('Problema a resolver'),
    p('O estudante precisa consultar os materiais da disciplina, esclarecer dúvidas e retomar explicações sem perder o contexto. O MVP concentra esse percurso em uma plataforma com acesso autenticado, fontes consultáveis e histórico.'),
    h('Proposta de valor'),
    p('<b>Estudar os materiais da disciplina com apoio de um Monitor Virtual que explica, apresenta referências e acompanha a conversa.</b> O objetivo do piloto é verificar se esse percurso ajuda o aluno e se as respostas se mantêm apoiadas nas fontes.'),
    h('Público inicial'),
    p('Estudantes das disciplinas contempladas e professores que revisem os conteúdos e as respostas. A quantidade de participantes e a turma do piloto devem ser definidas pela equipe.'),
    table(['Base funcional disponível','Escopo proposto para o piloto'],[
    ['Estatística e Estrutura de Dados Avançada acessíveis no catálogo conferido; Monitor Virtual, materiais e histórico integrados localmente.','Começar com essas duas disciplinas, após revisão acadêmica e preparação do ambiente. Expandir para Design e Ideação após completar o catálogo.']],[253.5,253.5]),Spacer(1,15),
    h('Situação deste documento'),
    p('Este PDF especifica o MVP; não é uma nova implementação nem uma comprovação de publicação. Os itens existentes refletem os registros do projeto. Metas e etapas futuras são propostas sujeitas ao alinhamento da equipe.'),PageBreak()]

mvp += page('02 / ESCOPO','Funcionalidades essenciais')
mvp += [table(['Funcionalidade','Comportamento esperado','Situação registrada'],[
    ['Acesso autenticado','Usar conta ativa e manter as conversas separadas entre estudantes.','Implementado localmente.'],
    ['Catálogo','Selecionar disciplina e, quando necessário, assunto.','Estatística e ED disponíveis; Design e Ideação pendentes no catálogo.'],
    ['Materiais','Consultar materiais cadastrados e abrir o arquivo citado quando disponível.','Integrado; permissões verificadas na abertura.'],
    ['Monitor Virtual','Enviar pergunta, receber explicação e referências aos materiais recuperados.','Implementado e validado em amostras.'],
    ['Continuidade','Pedir outra explicação, um exemplo ou um esquema na mesma conversa.','Até oito mensagens recentes contextualizam a pergunta.'],
    ['Histórico','Reabrir perguntas, respostas e fontes da própria conta.','Persistência e isolamento registrados.'],
    ['Feedback','Avaliar a plataforma voluntariamente com nota e comentário opcional.','Documentado na interface e no backend.']],[103,264,140]),Spacer(1,14),
    h('Fora do compromisso inicial do MVP'),
    p('Monitoria humana e agendamentos; geração de imagens; memória ilimitada entre conversas; catálogo de disciplinas além das contempladas; prática de ED sem listas ou provas autorizadas. Entrega progressiva de texto é melhoria posterior, salvo se o piloto revelar necessidade prioritária.'),
    h('Expansão após o núcleo'),
    p('A base da IA já contém Design e Ideação, mas a expansão exige cadastro completo na interface e conferência do percurso de estudo. A prática de ED depende de materiais elegíveis, autorização e validação específica.'),PageBreak()]

mvp += page('03 / ACEITE','Jornada e critérios do piloto')
mvp += [h('Percurso mínimo do estudante'),
    p('<b>1.</b> Entrar com uma conta ativa.<br/><b>2.</b> Escolher uma disciplina e consultar um material.<br/><b>3.</b> Fazer uma pergunta ao Monitor Virtual.<br/><b>4.</b> Conferir a referência e pedir uma nova explicação.<br/><b>5.</b> Reabrir a conversa no histórico.<br/><b>6.</b> Registrar uma avaliação, se desejar.'),
    table(['Critério de aceite proposto','Como demonstrar'],[
    ['Percurso completo disponível','Executar a jornada acima no ambiente do piloto, nas duas disciplinas iniciais.'],
    ['Respostas com fontes verificáveis','Conferir pergunta, resposta, material e página com roteiro revisado pelo professor.'],
    ['Continuidade útil','Pedir “explique melhor”, outro exemplo e mudança explícita de tema; conferir o contexto e as novas fontes.'],
    ['Tratamento da falta de conteúdo','Sem fontes suficientes, não apresentar resposta como fundamentada; solicitar esclarecimento quando necessário.'],
    ['Privacidade e permissões','Uma conta não abre o histórico de outra; materiais inativos ou não autorizados ao contexto não são usados.'],
    ['Uso em celular e computador','Conferir navegação, leitura, envio, fontes e reabertura de conversa nos dispositivos do piloto.'],
    ['Operação mínima','Demonstrar recuperação de backup e ausência de falhas impeditivas no teste simultâneo planejado.']],[196,311]),Spacer(1,12),
    p('Os testes locais existentes são evidências de partida. Os critérios acima precisam ser conferidos no ambiente e nas condições reais do piloto antes de sua liberação.','Small'),PageBreak()]

mvp += page('04 / EXECUÇÃO','Plano de lançamento e avaliação')
mvp += [table(['Etapa','Entrega esperada','Papel sugerido'],[
    ['1. Alinhar o escopo','Aprovar disciplinas iniciais, materiais, participantes, responsáveis e critérios de aceite.','Coordenação + professores'],
    ['2. Revisar o conteúdo','Preparar perguntas e respostas de referência; conferir referências e disponibilidade dos PDFs.','Professores + desenvolvimento'],
    ['3. Preparar o ambiente','Configurar hospedagem, banco, serviços, credenciais, backups e monitoramento.','Desenvolvimento + infraestrutura'],
    ['4. Conferir a versão','Executar a jornada, controles de acesso e teste com o número de acessos definido. Corrigir bloqueios.','Desenvolvimento + validação'],
    ['5. Rodar o piloto','Acompanhar uso, revisar amostras de respostas e recolher feedback dos participantes.','Coordenação + alunos + professores'],
    ['6. Decidir a expansão','Analisar resultados e priorizar catálogo de Design/Ideação, prática e melhorias.','Equipe do projeto']],[83,292,132]),Spacer(1,12),
    h('Indicadores a acompanhar'),
    p('Conclusão da jornada; respostas consideradas corretas e bem fundamentadas pelos professores; falhas de envio e acesso; tempo de resposta; avaliação dos estudantes; custo por interação. Definir metas e tamanho da amostra antes do piloto, pois ainda não há resultados reais desses indicadores.'),
    h('Condição proposta para iniciar'),
    p('Liberar o piloto quando os critérios essenciais da página anterior forem conferidos, não houver falhas que impeçam o uso e a equipe tiver definido quem acompanha o ambiente e recebe os relatos dos participantes.'),
    p('Planejamento sem datas ou responsáveis nominais presumidos. Base: relatório de desenvolvimento de 28/10/2026 e documentos internos de conversa com contexto, integração de ED e interface/histórico.','Small')]

paths=[build('NEURON_Relatorio_Equipe_2026-10-28.pdf','Relatório de desenvolvimento',report),build('NEURON_MVP_2026-10-28.pdf','MVP - proposta para piloto',mvp)]
for path in paths:
    reader=PdfReader(path)
    text='\n'.join(pg.extract_text() or '' for pg in reader.pages)
    assert len(reader.pages)==4,(path,len(reader.pages))
    assert len(text)>5000
    assert '\ufffd' not in text
    print(f'{path.name}: {len(reader.pages)} páginas; {len(text)} caracteres; {path.stat().st_size} bytes')
