from pathlib import Path
import re
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

ROOT=Path('C:/Projeto Extensionista 2/NEURON')
BASE='NEURON_Relatorio_Desenvolvimento_Validacao_2026-10-28'
SRC=ROOT/'output/pdf'/(BASE+'.md')
NAVY=colors.HexColor('#142D52')
pdfmetrics.registerFont(TTFont('Local','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('LocalB','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Local',normal='Local',bold='LocalB',italic='Local',boldItalic='LocalB')
ST={k:ParagraphStyle(k,fontName='LocalB' if k.startswith('h') else 'Local',fontSize=size,leading=lead,spaceBefore=before,spaceAfter=after,textColor=NAVY)
    for k,size,lead,before,after in [('p',9,13,0,7),('h1',23,28,0,14),('h2',17,22,0,14),('h3',11,15,9,6),('cell',8,11,0,0),('small',8,11,0,5)]}
def paragraph(text,style='p'):
    text=text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return Paragraph(re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text),ST[style])
def frame(c,d):
    w,h=A4
    c.saveState()
    c.setFillColor(NAVY);c.rect(0,h-32,w,32,fill=1,stroke=0)
    c.setFillColor(colors.white);c.setFont('LocalB',8.5);c.drawString(48,h-21,'NEURON / RELATÓRIO DE DESENVOLVIMENTO')
    c.setStrokeColor(colors.HexColor('#D9E2EC'));c.line(48,39,w-48,39)
    c.setFillColor(colors.HexColor('#52677C'));c.setFont('Local',8)
    c.drawString(48,25,'28/10/2026 • Ambiente local • Evidências da entrega');c.drawRightString(w-48,25,str(d.page))
    c.restoreState()
lines=SRC.read_text(encoding='utf-8').splitlines();flow=[];i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line=='<!-- page -->':flow.append(PageBreak());i+=1;continue
    if line.startswith('|'):
        raw=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            row=[s.strip() for s in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',v.replace(' ','')) for v in row):raw.append(row)
            i+=1
        n=len(raw[0]);widths=[180,319] if n==2 else [145,78,276]
        cells=[[paragraph('**'+v+'**' if j==0 else v,'cell') for v in row] for j,row in enumerate(raw)]
        t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EDF5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.8,NAVY),('LINEBELOW',(0,1),(-1,-1),.4,colors.HexColor('#DAE4EE')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8FA')])]))
        flow.extend([t,Spacer(1,7)]);continue
    if line.startswith('!['):
        path=(SRC.parent/re.search(r'\]\((.*?)\)',line).group(1)).resolve()
        w,h=ImageReader(str(path)).getSize()
        flow.extend([Image(str(path),width=459,height=459*h/w),Spacer(1,6)]);i+=1;continue
    if line.startswith('### '):flow.append(paragraph(line[4:],'h3'))
    elif line.startswith('## '):flow.append(paragraph(line[3:],'h2'))
    elif line.startswith('# '):flow.append(paragraph(line[2:],'h1'))
    elif line.startswith('- '):flow.append(paragraph('• '+line[2:],'small' if line.startswith('- E') or 'pendências' in ''.join(lines[max(0,i-6):i]) else 'p'))
    else:flow.append(paragraph(line,'small' if line.startswith('Figura ') else 'p'))
    i+=1
w,h=A4
doc=BaseDocTemplate(str(SRC.with_suffix('.pdf')),pagesize=A4,title='NEURON - Relatório de desenvolvimento e validação',author='Projeto NEURON')
doc.addPageTemplates(PageTemplate(id='relatorio',frames=[Frame(48,51,w-96,h-102,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=frame))
doc.build(flow)
print('Relatorio atualizado.')
