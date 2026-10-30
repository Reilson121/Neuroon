import json
import re
import subprocess
import urllib.request
from pathlib import Path

base = 'https://neuron-45-159-173-74.sslip.io'
def fetch(path):
    with urllib.request.urlopen(base + path, timeout=30) as response:
        assert response.status == 200
        return response.read().decode()

html = fetch('/')
js_path = re.search(r'src="(/assets/[^\"]+\.js)"', html).group(1)
css_path = re.search(r'href="(/assets/[^\"]+\.css)"', html).group(1)
js, css = fetch(js_path), fetch(css_path)
assert 'katex' in js and 'katex-display' in css and 'KaTeX_Main' in css
print('INTERFACE_HTTPS_COM_MATEMATICA_OK', flush=True)
code = r'''
import json,re
from app.rag.monitor_virtual import MonitorVirtual
r=MonitorVirtual().responder(
    'Explique passo a passo o limite de (x^2 - 1)/(x - 1) quando x tende a 1, usando fatoração. Escreva as frações em notação matemática.',
    'calculo_para_computacao_1')
assert not r['fallback'], r.get('motivo')
assert r['fontes']
assert re.search(r'\\[dt]?frac\{', r['resposta']), r['resposta']
assert '$' in r['resposta']
print('MATH_RESULT='+json.dumps({'resposta':r['resposta'],'fontes':len(r['fontes']),'fallback':r['fallback']},ensure_ascii=False))
'''
result = subprocess.run(
    ['docker','compose','--env-file','deploy/.env','-f','deploy/compose.yaml',
     'exec','-T','ai','python','-c',code],
    capture_output=True,text=True,timeout=180)
if result.returncode:
    print(result.stdout[-4000:])
    print(result.stderr[-4000:])
    raise SystemExit(result.returncode)
line = next(line for line in result.stdout.splitlines() if line.startswith('MATH_RESULT='))
report = {'aprovado':True,'interface_js':js_path,'interface_css':css_path,
          'monitor':json.loads(line.split('=',1)[1])}
Path('/opt/neuron/verificacao-formatacao-matematica.json').write_text(
    json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('MONITOR_REAL_COM_FRACOES_E_FONTES_OK',flush=True)
print(json.dumps(report,ensure_ascii=False))
