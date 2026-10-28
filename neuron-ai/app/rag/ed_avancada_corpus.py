"""Corpus local de ED: preserva a extração já conferida e seus identificadores."""
import copy
import hashlib
import json
from pathlib import Path

from app.rag.mapas.estrutura_de_dados_avancada import MAPA

ROOT = Path(__file__).resolve().parents[2]
DISCIPLINA = MAPA['disciplina']
PREFIXO = f'local:materiais_academicos/periodo_03/{DISCIPLINA}/'


def carregar_validado():
    inventario = json.loads((ROOT / 'propostas/ed_avancada/inventario.json').read_text(encoding='utf-8'))
    corpus = ROOT / 'saidas_testes/estrutura_de_dados_avancada_aula_0_aula_1_aula_2.json'
    if hashlib.sha256(corpus.read_bytes()).hexdigest() != inventario['corpus_sha256']:
        raise ValueError('Corpus alterado; confira novamente a extração.')
    for arquivo in MAPA['arquivos']:
        origem = ROOT / 'materiais_academicos/periodo_03' / DISCIPLINA / arquivo
        if hashlib.sha256(origem.read_bytes()).hexdigest() != inventario['arquivos'][arquivo]:
            raise ValueError('PDF diverge do inventário conferido.')
    dados = json.loads(corpus.read_text(encoding='utf-8'))
    ids = set()
    for chunk in dados['chunks']:
        m = chunk['metadata']
        aula = MAPA['arquivos'].get(m['arquivo'])
        if (not aula or m['disciplina'] != DISCIPLINA or m['periodo'] != '03'
                or m['assunto'] not in aula['assuntos'] or chunk['chunk_id'] in ids
                or not chunk['conteudo'].strip()):
            raise ValueError('Proveniência de chunk inválida.')
        ids.add(chunk['chunk_id'])
        for pagina in [m['pagina'], *m.get('paginas_mescladas', [])]:
            if not any(inicio <= pagina <= fim for inicio, fim in aula['assuntos'][m['assunto']]):
                raise ValueError('Página fora do assunto.')
    return dados


def preparar_material(material, assuntos):
    arquivo = next((a for a in MAPA['arquivos'] if material['referencia_externa'] == PREFIXO + a), None)
    if arquivo is None or material['tipo'] != 'SLIDE_AULA':
        raise ValueError('Material não preparado para ED Avançada.')
    if not all(material[k] for k in ('ativo', 'disciplina_ativa', 'periodo_ativo', 'fonte_monitor_virtual')):
        raise ValueError('Fonte indisponível no catálogo.')
    chunks = copy.deepcopy([c for c in carregar_validado()['chunks'] if c['metadata']['arquivo'] == arquivo])
    for chunk in chunks:
        meta = chunk['metadata']
        assunto = assuntos.get(meta['assunto'])
        if not assunto or not assunto['ativo'] or assunto['disciplina_id'] != material['disciplina_id']:
            raise ValueError('Assunto indisponível ou de outra disciplina.')
        meta.update(material_id=material['id'], disciplina_id=material['disciplina_id'],
                    periodo_id=material['periodo_id'], assunto_id=assunto['id'],
                    titulo_material=material['titulo'], tipo_material='SLIDE_AULA',
                    fonte_monitor_virtual=True, disponivel_para_pratica=False,
                    autorizacao_professor=material['autorizacao_professor'])
    return chunks
