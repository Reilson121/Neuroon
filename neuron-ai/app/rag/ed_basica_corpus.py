"""Estrutura de Dados, período 02. A UP1 disponível tem apenas quatro objetivas."""
import copy
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DISCIPLINA = 'estrutura_de_dados'
PASTA = RAIZ / 'materiais_academicos/periodo_02' / DISCIPLINA
JSON_CHUNKS = RAIZ / 'saidas_testes/estrutura_de_dados_completa.json'
MATERIAIS = [
    ('fundamentos_c', 'Fundamentos da linguagem C'),
    ('logica_e_controle', 'Expressões, decisões, repetições e escopo'),
    ('vetores_e_matrizes', 'Estruturas de dados, vetores e matrizes'),
    ('registros', 'Registros e typedef'),
    ('ponteiros', 'Ponteiros e passagem de endereços'),
    ('listas', 'Listas encadeadas'),
    ('filas', 'Filas, fila circular e deque'),
    ('pilhas', 'Pilhas'),
    ('arvores_e_grafos', 'Introdução a árvores e grafos'),
]


def consolidar():
    import pymupdf
    from app.rag.chunk_processor import ChunkProcessor
    arquivos, paginas, chunks = [], [], []
    for i, (slug, titulo) in enumerate(MATERIAIS, 1):
        encontrados = list(PASTA.glob(f'UNIT_EDD_{i:02d}*.pdf'))
        if len(encontrados) != 1:
            raise ValueError(f'Esperado um PDF para a unidade {i}.')
        pdf = encontrados[0]
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        arquivos.append(dict(assunto=slug, titulo=titulo, arquivo=pdf.name,
            pdf=pdf.relative_to(RAIZ).as_posix(), pdf_sha256=digest, tipo='SLIDE_AULA'))
        with pymupdf.open(pdf) as doc:
            for n, p in enumerate(doc, 1):
                texto = p.get_text().replace('\x00', '').strip()
                if not texto:
                    continue  # Página de figura: o original continua disponível para consulta.
                paginas.append(dict(conteudo=texto, metadata=dict(periodo='02', disciplina=DISCIPLINA,
                    assunto=slug, aula=None, arquivo=pdf.name, pagina=n, tipo_arquivo='pdf',
                    tipo_extracao='textual', tipo_material='SLIDE_AULA', pdf_sha256=digest,
                    titulo_material=titulo)))
    chunks.extend(ChunkProcessor().processar_resultados(paginas))
    pdf = PASTA / 'prova_estrutura_de_dados_transcrita.pdf'
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    arquivos.append(dict(assunto=None, titulo='UP1 — prova transcrita (parcial)', arquivo=pdf.name,
        pdf=pdf.relative_to(RAIZ).as_posix(), pdf_sha256=digest, tipo='PROVA_ANTIGA'))
    # Preserva enunciado e alternativas efetivamente recebidos; não inventa as duas abertas.
    import re
    with pymupdf.open(pdf) as doc:
        for pagina, p in enumerate(doc, 1):
            partes = re.split(r'Questão\s+(\d+):\s*\(1 ponto\)', p.get_text())
            for j in range(1, len(partes), 2):
                numero, texto = int(partes[j]), partes[j+1].strip()
                itens = re.split(r'\[\s*\]\s*([a-e])\)', texto)
                if len(itens) != 11:
                    raise ValueError('Transcrição da prova precisa de revisão.')
                slug = {1:'fundamentos_c', 2:'fundamentos_c', 3:'vetores_e_matrizes', 4:'vetores_e_matrizes'}[numero]
                q = dict(referencia_local=f'estrutura_de_dados_up1_q{numero}',
                    formato_original='multipla_escolha', assunto_principal_proposto=slug,
                    enunciado=itens[0].strip(), alternativas={itens[k].upper():itens[k+1].strip() for k in range(1,11,2)},
                    gabarito_material=None)
                meta = dict(periodo='02', disciplina=DISCIPLINA, assunto=slug, aula=None,
                    arquivo=pdf.name, pagina=pagina, tipo_arquivo='pdf', tipo_extracao='textual',
                    tipo_material='PROVA_ANTIGA', pdf_sha256=digest, numero_questao=str(numero),
                    titulo_material='UP1 — prova transcrita (parcial)', chunk_index=numero-1)
                chunks.append(dict(chunk_id=hashlib.sha256(f'{DISCIPLINA}|{digest}|q{numero}'.encode()).hexdigest()[:24],
                    conteudo=json.dumps(q, ensure_ascii=False), metadata=meta))
    if sum(c['metadata']['tipo_material']=='PROVA_ANTIGA' for c in chunks) != 4:
        raise ValueError('Esperadas quatro questões transcritas.')
    return dict(disciplina=DISCIPLINA, periodo='02', arquivos=arquivos, paginas=paginas,
        chunks=chunks, total_paginas=len(paginas)+2, total_chunks=len(chunks),
        prova=dict(unidade=1, objetivas_disponiveis=4, abertas_ausentes=2, gabarito_oficial=False))


def carregar_validado():
    dados = json.loads(JSON_CHUNKS.read_text(encoding='utf-8'))
    for a in dados['arquivos']:
        if hashlib.sha256((RAIZ/a['pdf']).read_bytes()).hexdigest() != a['pdf_sha256']:
            raise ValueError('PDF diverge do corpus de Estrutura de Dados.')
    return dados


def preparar_material(m, assuntos):
    from app.practice.material_index import permitido
    if m.get('disciplina_slug') != DISCIPLINA or m['periodo_numero'] != 2 or not permitido(m):
        raise ValueError('Material fora do segundo período ou indisponível.')
    dados = carregar_validado()
    origem = next((a for a in dados['arquivos'] if m['referencia_externa']=='local:'+a['pdf']), None)
    if not origem or origem['tipo'] != m['tipo']:
        raise ValueError('Material fora do corpus de Estrutura de Dados.')
    if origem['assunto'] is not None and m['assunto_id'] != assuntos[origem['assunto']]['id']:
        raise ValueError('Assunto incompatível com o PDF.')
    chunks = copy.deepcopy([c for c in dados['chunks'] if c['metadata']['arquivo']==origem['arquivo']])
    for c in chunks:
        meta = c['metadata']; a = assuntos[meta['assunto']]
        if not a['ativo'] or a['disciplina_id'] != m['disciplina_id']:
            raise ValueError('Assunto indisponível ou de outra disciplina.')
        meta.update(material_id=m['id'], periodo_id=m['periodo_id'], disciplina_id=m['disciplina_id'],
            assunto_id=a['id'], fonte_monitor_virtual=m['fonte_monitor_virtual'],
            autorizacao_professor=m['autorizacao_professor'], disponivel_para_pratica=m['disponivel_para_pratica'])
    return chunks
