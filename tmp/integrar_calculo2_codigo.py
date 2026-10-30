from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def edit(path,old,new):
    p=ROOT/path;text=p.read_text(encoding='utf-8')
    if old not in text:raise ValueError(f'Trecho ausente: {path}: {old[:80]}')
    p.write_text(text.replace(old,new),encoding='utf-8')

p='neuron-ai/app/practice/service.py'
edit(p,"if any(r.get('disciplina_slug')=='calculo_para_computacao_1' for r in refs):\n            from app.practice.calculo_engine import TOPICOS", "if any(r.get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'} for r in refs):\n            if refs[0]['disciplina_slug']=='calculo_para_computacao_2':\n                from app.practice.integral_engine import TOPICOS\n            else:\n                from app.practice.calculo_engine import TOPICOS")
edit(p,"elif grupos[slug][0].get('disciplina_slug') == 'calculo_para_computacao_1':\n                        from app.practice.calculo_engine import gerar as gerar_calculo", "elif grupos[slug][0].get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'}:\n                        if grupos[slug][0]['disciplina_slug']=='calculo_para_computacao_2':\n                            from app.practice.integral_engine import gerar as gerar_calculo\n                        else:\n                            from app.practice.calculo_engine import gerar as gerar_calculo")
edit(p,"if req.get('assunto_ids') and any(r.get('disciplina_slug')=='calculo_para_computacao_1' for r in refs):", "if req.get('assunto_ids') and any(r.get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'} for r in refs):")
edit(p,"not in {'calculo','sistemas_digitais'", "not in {'calculo','integral','sistemas_digitais'")
p='neuron-ai/app/practice/math_engine.py'
edit(p,"    if q.get('spec', {}).get('motor') == 'calculo':", "    if q.get('spec', {}).get('motor') == 'integral':\n        from app.practice.integral_engine import verificar as verificar_integral\n        return verificar_integral(q)\n    if q.get('spec', {}).get('motor') == 'calculo':")
p='neuron-ai/app/practice/material_index.py'
edit(p,"{'calculo_para_computacao_1',", "{'calculo_para_computacao_2', 'calculo_para_computacao_1',")
edit(p,"m.get('disciplina_slug') == 'calculo_para_computacao_1'", "m.get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'}")
edit(p,"    if disciplina == 'calculo_para_computacao_1':", "    if disciplina == 'calculo_para_computacao_2':\n        from app.rag.integral_corpus import preparar_material\n        chunks = preparar_material(m, assuntos)\n    elif disciplina == 'calculo_para_computacao_1':")
p='neuron-ai/app/practice/repository.py'
edit(p,"'calculo_para_computacao_1','estrutura_de_dados_avancada'", "'calculo_para_computacao_1','calculo_para_computacao_2','estrutura_de_dados_avancada'")
edit(p,"(d.slug IN ('estrutura_de_dados_avancada','design_de_artefatos_digitais') AND p.numero=3)", "(d.slug IN ('estrutura_de_dados_avancada','design_de_artefatos_digitais','calculo_para_computacao_2') AND p.numero=3)")
edit(p,"d.slug<>'calculo_para_computacao_1' AND m.tipo='SLIDE_AULA'", "d.slug NOT IN ('calculo_para_computacao_1','calculo_para_computacao_2') AND m.tipo='SLIDE_AULA'")
edit(p,"OR (d.slug='calculo_para_computacao_1' AND\n                       ((m.tipo", "OR (d.slug IN ('calculo_para_computacao_1','calculo_para_computacao_2') AND\n                       ((m.tipo")
p='neuron-ai/app/rag/retriever.py'
edit(p,'"sistemas_digitais", "calculo_para_computacao_1"}', '"sistemas_digitais", "calculo_para_computacao_1", "calculo_para_computacao_2"}')
edit(p,"            if disciplina.strip() == 'calculo_para_computacao_1':", "            if disciplina.strip() == 'calculo_para_computacao_2':\n                from app.rag.integral_search import ordenar_evidencias\n                candidatos=self.store.buscar_hibridos(embedding,consulta_lexical,disciplina.strip(),assunto=filtros['assunto'],k=50)\n                linhas=ordenar_evidencias(candidatos,pergunta,k,assunto)\n            elif disciplina.strip() == 'calculo_para_computacao_1':")
p='neuron-ai/app/rag/monitor_virtual.py'
edit(p,'Você é o Monitor Virtual do NEURON, um tutor conversacional.', '''Você é o Monitor Virtual do NEURON, um tutor conversacional.
Cálculo para Computação II (calculo_para_computacao_2) é do TERCEIRO período.
Segundo o escopo informado pelo aluno, a unidade 1 tem SOMENTE integrais de uma
variável: primitivas, indefinidas e definidas. A unidade 2 é organizada como
integrais duplas e triplas por cálculo direto em cartesianas, com limites dados.
Não há prova oficial nesta disciplina. Simulados são autorais, com comandos diretos
inspirados no FORMATO da prova de Cálculo I, sem atribuir integrais àquela prova.
O guia recebido de funções de várias variáveis foi criado com IA e é COMPLEMENTAR:
domínio, avaliação e variáveis fixas dão base. Gradiente, parciais, otimização,
Lagrange e mudanças de coordenadas não são cobrança confirmada nem parte dos
simulados padrão. Explique esses temas só como complemento quando solicitados.
Os PDFs Guia de Integrais e Tabela de Integrais são apoios autorais NEURON com IA,
não materiais emitidos pelo professor. Sugira consulta à Tabela de Integrais.
Em integrais, mostre fórmula, primitiva, C nas indefinidas e F(b)-F(a) nas definidas.
Em duplas e triplas, mostre cada etapa, trate outras variáveis como constantes e
respeite os diferenciais. Nunca troque limites ou acrescente C em etapas definidas.''')
p='backend/demo/src/main/java/com/Neuron/demo/pratica/PraticaService.java'
edit(p,'"calculo_para_computacao_1".equals(d.getSlug()) && d.getPeriodo().getNumero()==2', '("calculo_para_computacao_1".equals(d.getSlug()) && d.getPeriodo().getNumero()==2 || "calculo_para_computacao_2".equals(d.getSlug()) && d.getPeriodo().getNumero()==3)')

# O mesmo componente de prova mantém a correção somente após a entrega.
p='frontend/src/components/CalculoPratica.jsx'
edit(p,"import topicos from '../calculo-topicos.json';", "import topicosI from '../calculo-topicos.json';\nimport topicosII from '../integral-topicos.json';")
edit(p," const [tipo,setTipo]", " const integral=disciplina.nome==='Cálculo para Computação II';\n const topicos=integral?topicosII:topicosI;\n const [tipo,setTipo]")
edit(p,"topicos.filter(t=>!unidade||t.unidade===unidade)", "topicos.filter(t=>(!integral||t.unidade>0)&&(!unidade||t.unidade===unidade))")
edit(p,"{simulado&&<>\n    <p>", "{simulado&&<>\n    {integral?<p className=\"notice\">Simulado autoral de estudo: esta disciplina não tem prova oficial. Comandos diretos inspirados no formato de Cálculo I, adaptados para cinco alternativas. A 1ª unidade cobra somente integrais de uma variável; a 2ª reúne duplas e triplas diretas em cartesianas. O complemento de várias variáveis fica fora dos simulados padrão.</p>:<>\n    <p>")
edit(p,"sem garantia de reproduzir a avaliação oficial.</p>", "sem garantia de reproduzir a avaliação oficial.</p></>}")
edit(p,"topicos.some(t=>t.assuntoOrdem===a.ordem)", "topicos.some(t=>(!integral||t.unidade>0)&&t.assuntoOrdem===a.ordem)")
p='frontend/src/components/CalculoFiltros.jsx'
edit(p,"import topicos from '../calculo-topicos.json';", "import topicosI from '../calculo-topicos.json';\nimport topicosII from '../integral-topicos.json';")
edit(p,"origem='MISTO'}){", "origem='MISTO',integral=false}){\n const topicos=integral?topicosII:topicosI;")
edit(p,"{u===1?'1ª unidade · Funções e limites':'2ª unidade · Derivadas'}", "{integral?(u===1?'1ª unidade · Integrais de uma variável':'2ª unidade · Integrais duplas e triplas'):(u===1?'1ª unidade · Funções e limites':'2ª unidade · Derivadas')}")
p='frontend/src/App.jsx'
edit(p,"if(disciplina.nome==='Cálculo para Computação I')return", "if(['Cálculo para Computação I','Cálculo para Computação II'].includes(disciplina.nome))return")
edit(p," const calculo=disciplina.nome==='Cálculo para Computação I';", " const integral=disciplina.nome==='Cálculo para Computação II';\n const calculo=integral||disciplina.nome==='Cálculo para Computação I';")
edit(p,"m.titulo.includes('Tabela de Derivadas')", "m.titulo.includes(integral?'Tabela de Integrais':'Tabela de Derivadas')")
edit(p,"{!edAvancada&&<option value=\"CADASTRADAS\">", "{!edAvancada&&!integral&&<option value=\"CADASTRADAS\">")
edit(p,"calculo?'Livros, tabela e prova da 1ª unidade'", "integral?'Guia autoral e tabela de integrais':calculo?'Livros, tabela e prova da 1ª unidade'")
edit(p,"{!edAvancada&&<>", "{!edAvancada&&!integral&&<>")
edit(p,"<CalculoFiltros valor=", "<CalculoFiltros integral={integral} valor=")
edit(p,"{calculo&&<p className=\"notice\">Cálculo para Computação I", "{calculo&&!integral&&<p className=\"notice\">Cálculo para Computação I")
edit(p,"{calculo&&<p className=\"tip\">Ao resolver derivadas", "{integral&&<><p className=\"notice\">Cálculo para Computação II · 3º período. A 1ª unidade contém apenas integrais de uma variável; a 2ª reúne integrais duplas e triplas por cálculo direto. A disciplina não tem prova oficial. Funções de várias variáveis são um complemento opcional, fora dos simulados padrão.</p><p className=\"tip\">Consulte a Tabela de Integrais - apoio autoral NEURON. {tabela?.arquivoDisponivel&&<a href={`/api/v1/materiais/${tabela.id}/arquivo`} target=\"_blank\" rel=\"noopener noreferrer\">Abrir tabela de integrais</a>}</p></>}\n {calculo&&!integral&&<p className=\"tip\">Ao resolver derivadas")

# Catálogo compartilhado entre o gerador e a interface.
import sys
sys.path.insert(0,str(ROOT/'neuron-ai'))
from app.practice.integral_engine import TOPICOS
from scripts.preparar_calculo2 import ASSUNTOS,PASTA
topicos=[dict(id=t,assunto=v[0],unidade=v[1],nome=v[2],tipos=v[3],assuntoOrdem=[a[0] for a in ASSUNTOS].index(v[0])+1) for t,v in TOPICOS.items()]
(ROOT/'frontend/src/integral-topicos.json').write_text(json.dumps(topicos,ensure_ascii=False,indent=2),encoding='utf-8')
def sql(v):return "'"+v.replace("'","''")+"'"
lines=["-- possui_prova habilita prática na plataforma; não indica prova oficial.","INSERT INTO periodo(numero,nome,ordem) VALUES(3,'3º período',3) ON CONFLICT(numero) DO NOTHING;",
 "INSERT INTO disciplina(periodo_id,nome,slug,descricao,possui_prova) SELECT id,'Cálculo para Computação II','calculo_para_computacao_2','Unidade 1: integrais de uma variável. Unidade 2 proposta: duplas e triplas diretas. Sem prova oficial; simulados autorais e complemento opcional.',TRUE FROM periodo WHERE numero=3 ON CONFLICT(slug) DO NOTHING;"]
for ordem,(slug,nome) in enumerate(ASSUNTOS,1):
    lines.append(f"INSERT INTO assunto(disciplina_id,nome,slug,descricao,ordem) SELECT id,{sql(nome)},{sql(slug)},{sql('Complemento opcional criado com IA, fora da cobrança e dos simulados padrão.' if ordem==8 else 'Cálculo direto conforme escopo informado; apoio autoral de estudo.')},{ordem} FROM disciplina WHERE slug='calculo_para_computacao_2' ON CONFLICT(disciplina_id,slug) DO NOTHING;")
for f in sorted(PASTA.glob('*.pdf')):
    ref='local:'+f.relative_to(ROOT/'neuron-ai').as_posix()
    desc='Complemento amplo criado com IA e fornecido pelo aluno. Não é conteúdo cobrado pelo professor.' if f.name.startswith('funçoes') else 'Apoio autoral NEURON com IA. Não é material nem prova oficial do professor.'
    assunto="(SELECT a.id FROM assunto a WHERE a.disciplina_id=d.id AND a.slug='base_multivariavel')" if f.name.startswith('funçoes') else 'NULL'
    lines.append(f"INSERT INTO material(disciplina_id,assunto_id,titulo,descricao,tipo,referencia_externa,fonte_monitor_virtual,disponivel_para_pratica,autorizacao_professor) SELECT d.id,{assunto},{sql(f.stem)},{sql(desc)},'RESUMO',{sql(ref)},TRUE,FALSE,FALSE FROM disciplina d WHERE slug='calculo_para_computacao_2' AND NOT EXISTS(SELECT 1 FROM material m WHERE m.disciplina_id=d.id AND m.referencia_externa={sql(ref)});")
(ROOT/'backend/demo/src/main/resources/db/migration/V13__catalogo_calculo_2.sql').write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Reusa o indexador por disciplina, com a validação do novo corpus e período.
text=(ROOT/'neuron-ai/scripts/integrar_materiais_calculo.py').read_text(encoding='utf-8')
text=text.replace('app.rag.calculo_corpus','app.rag.integral_corpus').replace('V11','V13').replace("!='02'","!='03'").replace('segundo período','terceiro período').replace('periodo=2','periodo=3').replace('calculo_integracao.json','calculo2_integracao.json')
(ROOT/'neuron-ai/scripts/integrar_materiais_calculo2.py').write_text(text,encoding='utf-8')
