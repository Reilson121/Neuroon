"""Cálculo para Computação I, segundo período: livros, tabela e UP1 recebida."""
import copy
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DISCIPLINA = 'calculo_para_computacao_1'
PASTA = RAIZ / 'materiais_academicos/periodo_02' / DISCIPLINA
JSON_CHUNKS = PASTA / 'corpus.json'
# Intervalos são páginas do PDF, não a numeração impressa dos livros.
ASSUNTOS = [
    ('funcoes_compostas', '1ª unidade · Funções compostas', 'Composição, ordem, domínio e decomposição.'),
    ('funcoes_inversas', '1ª unidade · Funções inversas', 'Injetividade, sobrejetividade, bijetividade, inversa e gráficos.'),
    ('simplificacao_algebrica', '1ª unidade · Simplificação algébrica', 'Fator comum, produtos notáveis, cancelamento e restrições do domínio.'),
    ('limites', '1ª unidade · Limites', 'Conceito, propriedades, substituição, indeterminações, confronto, definição precisa e infinito.'),
    ('continuidade', '1ª unidade · Limites laterais e continuidade', 'Limites laterais, funções por partes e continuidade no ponto.'),
    ('derivada_definicao', '2ª unidade · Definição de derivada', 'Quociente incremental, reta tangente, taxa instantânea e derivabilidade.'),
    ('regras_derivacao', '2ª unidade · Regras de derivação', 'Constante, potência, soma, produto, quociente, cadeia, trigonométricas, exponenciais, logaritmos e hiperbólicas.'),
    ('derivacao_implicita', '2ª unidade · Derivação implícita', 'Derivação de relações e funções inversas.'),
    ('aplicacoes_derivada', '2ª unidade · Aplicações da derivada', 'Taxas de variação, crescimento e decaimento, taxas relacionadas, aproximação linear e diferenciais.'),
]


def assunto_pagina(nome, pagina):
    if nome.startswith('01 '): return ['funcoes_compostas'] if pagina <= 9 else ['funcoes_inversas']
    if nome.startswith('02 '):
        if pagina >= 57: return ['derivada_definicao','aplicacoes_derivada'] if pagina<=62 else ['derivada_definicao']
        return ['continuidade'] if 35 <= pagina <= 44 else ['limites']
    if nome.startswith('03 '):
        if 32 <= pagina <= 39: return ['derivacao_implicita']
        if 45 <= pagina <= 75: return ['aplicacoes_derivada']
        return ['regras_derivacao']
    if nome.startswith('Tabela'): return ['regras_derivacao']
    return ['funcoes_compostas', 'funcoes_inversas', 'simplificacao_algebrica', 'limites', 'continuidade']


def consolidar():
    import pymupdf
    from app.rag.chunk_processor import ChunkProcessor
    arquivos, paginas, chunks = [], [], []
    fontes = [p for p in PASTA.glob('*.pdf') if p.name.startswith(('01 ', '02 ', '03 ', 'Tabela', 'prova_calculo'))]
    if len(fontes) != 5: raise ValueError('Esperados três livros, uma tabela e a prova transcrita da UP1.')
    for pdf in sorted(fontes):
        tipo = 'PROVA_ANTIGA' if pdf.name.startswith('prova') else 'RESUMO' if pdf.name.startswith('Tabela') else 'TRECHO_LIVRO'
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        with pymupdf.open(pdf) as doc:
            arquivos.append(dict(arquivo=pdf.name, pdf=pdf.relative_to(RAIZ).as_posix(), pdf_sha256=digest,
                titulo=pdf.stem, tipo=tipo, paginas=len(doc)))
            for n, page in enumerate(doc, 1):
                texto = page.get_text().replace('\x00', '').strip()
                if pdf.name.startswith('Tabela') and n==1:
                    # Conferida visualmente: os sobrescritos da fonte do PDF não têm
                    # mapeamento Unicode confiável na extração automática.
                    texto = '''Tabela de Derivadas do Prof. Douglas Maioli — página 1.
Seja a uma constante. Derivadas: (a)' = 0; (x)' = 1; (a*x)' = a;
(x^a)' = a*x^(a-1); (a^x)' = ln(a)*a^x; (e^x)' = e^x;
(log_a(x))' = 1/(x*ln(a)); (ln(x))' = 1/x;
(sen(x))' = cos(x); (cos(x))' = -sen(x); (tg(x))' = sec(x)^2;
(sec(x))' = tg(x)*sec(x); (cossec(x))' = -cotg(x)*cossec(x);
(cotg(x))' = -cossec(x)^2.
Fator constante: (a*f(x))' = a*f'(x).
Regra da soma e subtração: (f+g)' = f'+g'; (f-g)' = f'-g'.
Regra do produto: (f*g)' = f'*g + f*g'.
Regra do quociente: (f/g)' = (f'*g - f*g')/g^2.
Regra da cadeia: h(x) = f(g(x)) implica h'(x) = f'(g(x))*g'(x).'''
                if not texto: continue
                for slug in assunto_pagina(pdf.name, n):
                    unidade = 2 if slug in {'derivada_definicao', 'regras_derivacao', 'derivacao_implicita', 'aplicacoes_derivada'} else 1
                    meta = dict(periodo='02', disciplina=DISCIPLINA, unidade=unidade, assunto=slug, aula=None,
                        arquivo=pdf.name, pagina=n, tipo_arquivo='pdf', tipo_extracao='textual', tipo_material=tipo,
                        pdf_sha256=digest, titulo_material=pdf.stem)
                    if pdf.name.startswith('Tabela') and n==1:
                        meta.update(tipo_extracao='textual',transcricao_conferida=True,metodo_preparo='transcricao_conferida_visualmente')
                    # Texto integral preservado; prova aberta não é convertida em múltipla escolha.
                    paginas.append(dict(conteudo=texto, metadata=meta))
    chunks = ChunkProcessor().processar_resultados(paginas)
    for c in chunks:
        c['chunk_id']=hashlib.sha256((c['chunk_id']+'|'+c['metadata']['assunto']).encode()).hexdigest()[:24]
        c['metadata']['chunk_id']=c['chunk_id']
    # Fatoração aparece explicitamente na UP1; seus enunciados são contexto de estudo,
    # não um banco com gabarito oficial ou alternativas inventadas.
    return dict(disciplina=DISCIPLINA, periodo='02', arquivos=arquivos, paginas=paginas,
        chunks=chunks, total_paginas=sum(a['paginas'] for a in arquivos), total_chunks=len(chunks),
        prova=dict(unidade=1, unidade_2_disponivel=False, gabarito_oficial=False,
            observacao='A transcrição omite o item 2b e o valor em x=1 da questão 8A. Não reconstruir esses dados.'))


def carregar_validado():
    dados = json.loads(JSON_CHUNKS.read_text(encoding='utf-8'))
    for a in dados['arquivos']:
        if hashlib.sha256((RAIZ/a['pdf']).read_bytes()).hexdigest() != a['pdf_sha256']:
            raise ValueError('PDF de Cálculo diverge do corpus preparado.')
    return dados


def preparar_material(m, assuntos):
    from app.practice.material_index import permitido
    if m.get('disciplina_slug') != DISCIPLINA or m['periodo_numero'] != 2 or not permitido(m):
        raise ValueError('Cálculo exige material disponível do segundo período.')
    dados = carregar_validado()
    origem = next((a for a in dados['arquivos'] if m['referencia_externa']=='local:'+a['pdf']), None)
    if not origem or origem['tipo'] != m['tipo']: raise ValueError('Material fora do corpus de Cálculo.')
    chunks = copy.deepcopy([c for c in dados['chunks'] if c['metadata']['arquivo']==origem['arquivo']])
    for c in chunks:
        meta = c['metadata']; a = assuntos[meta['assunto']]
        if not a['ativo'] or a['disciplina_id'] != m['disciplina_id']: raise ValueError('Assunto indisponível.')
        meta.update(material_id=m['id'], periodo_id=m['periodo_id'], disciplina_id=m['disciplina_id'],
            assunto_id=a['id'], fonte_monitor_virtual=m['fonte_monitor_virtual'],
            autorizacao_professor=m['autorizacao_professor'], disponivel_para_pratica=m['disponivel_para_pratica'])
    return chunks
