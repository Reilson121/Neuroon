"""Fontes de Sistemas Digitais: doze PDFs, sem as cópias repetidas."""
import copy
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DISCIPLINA = 'sistemas_digitais'
PASTA = RAIZ / 'materiais_academicos/periodo_03' / DISCIPLINA
JSON_CHUNKS = RAIZ / 'saidas_testes/sistemas_digitais_completa.json'
MATERIAIS = [
    ('sistemas_analogicos_e_digitais', 'Sistemas analógicos e digitais.pdf'),
    ('portas_logicas_e_circuitos_digitais', 'Portas lógicas e circuitos digitais.pdf'),
    ('algebra_booleana', 'Álgebra booleana.pdf'),
    ('circuitos_logicos', 'Circuitos lógicos.pdf'),
    ('contadores', 'Contadores.pdf'),
    ('logica_sequencial', 'Lógica sequencial - Flip-flops e registradores.pdf'),
    ('maquinas_de_estados_finitos', 'Máquinas de estados finitos.pdf'),
    ('memoria_rom', 'Memória ROM.pdf'),
    ('memorias', 'Memórias - ROM, RAM, FIFO e LIFO.pdf'),
    ('circuitos_logicos_sequenciais', 'Circuitos lógicos sequenciais.pdf'),
    ('introducao_a_eletronica_digital', 'Introdução à eletrônica digital.pdf'),
    ('projetos_de_circuitos_sequenciais', 'Projetos de circuitos sequenciais.pdf'),
]
# Conferidas visualmente: contracapas, aviso editorial de fim do trecho e folhas brancas.
PAGINAS_EDITORIAIS = {
    'sistemas_analogicos_e_digitais': [15], 'portas_logicas_e_circuitos_digitais': [14, 15],
    'algebra_booleana': [22], 'circuitos_logicos': [17], 'contadores': [20, 21],
    'logica_sequencial': [20, 21], 'maquinas_de_estados_finitos': [16, 17],
    'memoria_rom': [11, 12], 'memorias': [2, 18], 'circuitos_logicos_sequenciais': [18, 19],
    'introducao_a_eletronica_digital': [11, 12], 'projetos_de_circuitos_sequenciais': [2],
}


def consolidar():
    import pymupdf
    from app.rag.chunk_processor import ChunkProcessor
    paginas, arquivos = [], []
    hashes = set()
    for slug, nome in MATERIAIS:
        pdf = PASTA / nome
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if digest in hashes:
            raise ValueError('PDF repetido no corpus.')
        hashes.add(digest)
        with pymupdf.open(pdf) as doc:
            arquivos.append(dict(assunto=slug, arquivo=nome, pdf=pdf.relative_to(RAIZ).as_posix(),
                                 pdf_sha256=digest, paginas=len(doc)))
            for numero, pagina in enumerate(doc, 1):
                texto = pagina.get_text().replace('\x00', '').strip()
                if numero in PAGINAS_EDITORIAIS[slug]:
                    continue
                if not texto:
                    raise ValueError(f'Página sem texto: {nome}, {numero}. Revisar extração.')
                paginas.append(dict(conteudo=texto, metadata=dict(periodo='03', disciplina=DISCIPLINA,
                    assunto=slug, aula=None, arquivo=nome, pagina=numero, tipo_arquivo='pdf',
                    tipo_extracao='textual', tipo_material='SLIDE_AULA', pdf_sha256=digest,
                    titulo_material=nome[:-4])))
    chunks = ChunkProcessor().processar_resultados(paginas)
    return dict(disciplina=DISCIPLINA, periodo='03', arquivos=arquivos, paginas=paginas,
                chunks=chunks, total_paginas=len(paginas), total_chunks=len(chunks))


def carregar_validado():
    salvo = json.loads(JSON_CHUNKS.read_text(encoding='utf-8'))
    if salvo != consolidar():
        raise ValueError('Corpus de Sistemas Digitais desatualizado; execute scripts.preparar_sistemas_digitais.')
    return salvo


def preparar_material(material, assuntos):
    if (material.get('disciplina_slug') != DISCIPLINA or material['tipo'] != 'SLIDE_AULA'
            or material['periodo_numero'] != 3 or not all(material[k] for k in
                ('ativo', 'disciplina_ativa', 'periodo_ativo', 'fonte_monitor_virtual'))):
        raise ValueError('Fonte de Sistemas Digitais indisponível.')
    dados = carregar_validado()
    origem = next((a for a in dados['arquivos'] if material['referencia_externa'] == 'local:' + a['pdf']), None)
    if origem is None:
        raise ValueError('PDF fora do corpus.')
    assunto = assuntos.get(origem['assunto'])
    if not assunto or not assunto['ativo'] or assunto['disciplina_id'] != material['disciplina_id'] or material['assunto_id'] != assunto['id']:
        raise ValueError('Assunto incompatível com o PDF.')
    chunks = copy.deepcopy([c for c in dados['chunks'] if c['metadata']['arquivo'] == origem['arquivo']])
    for c in chunks:
        c['metadata'].update(material_id=material['id'], periodo_id=material['periodo_id'],
            disciplina_id=material['disciplina_id'], assunto_id=assunto['id'],
            titulo_material=material['titulo'], fonte_monitor_virtual=True,
            autorizacao_professor=material['autorizacao_professor'], disponivel_para_pratica=False)
    return chunks
