from pathlib import Path
p=Path('output/deploy/verify-calculo2.py');t=p.read_text(encoding='utf-8')
t=t.replace('import hashlib,http.cookiejar,json,re,secrets,subprocess,time,urllib.request,uuid','import hashlib,http.cookiejar,json,re,secrets,subprocess,time,urllib.request,uuid,sys')
t=t.replace('report=dict(aprovado=False,checks=[]);csrf=None;created=False',"report=json.loads((ROOT/'verificacao-calculo2-publicado.json').read_text()) if '--monitor-only' in sys.argv else dict(checks=[]);report['aprovado']=False;csrf=None;created=False")
start=t.index(' amostras=[]');end=t.index(' monitor=[]',start)
t=t[:start]+" if '--monitor-only' not in sys.argv:\n"+''.join(' '+line+'\n' for line in t[start:end].splitlines())+t[end:]
t=t.replace('As funções de várias variáveis e o gradiente do complemento entram na cobrança dos simulados padrão de Cálculo II?','Explique o que é uma função de duas variáveis e calcule f(1,2) para f(x,y)=x^2+y.')
p.write_text(t,encoding='utf-8');compile(t,str(p),'exec')
