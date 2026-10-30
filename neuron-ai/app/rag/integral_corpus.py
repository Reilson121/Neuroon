"""Corpus de Cálculo II: materiais autorais e complemento fornecido pelo aluno."""
import copy
import hashlib
import json
from pathlib import Path

RAIZ=Path(__file__).resolve().parents[2]
DISCIPLINA='calculo_para_computacao_2'
PASTA=RAIZ/'materiais_academicos/periodo_03'/DISCIPLINA

def carregar_validado():
    dados=json.loads((PASTA/'corpus.json').read_text(encoding='utf-8'))
    for a in dados['arquivos']:
        if hashlib.sha256((RAIZ/a['pdf']).read_bytes()).hexdigest()!=a['pdf_sha256']:
            raise ValueError('Material de integrais diverge do corpus.')
    return dados

def preparar_material(m,assuntos):
    from app.practice.material_index import permitido
    if m.get('disciplina_slug')!=DISCIPLINA or m['periodo_numero']!=3 or not permitido(m):
        raise ValueError('Cálculo II exige material ativo do terceiro período.')
    dados=carregar_validado();origem=next((a for a in dados['arquivos'] if m['referencia_externa']=='local:'+a['pdf']),None)
    if not origem or origem['tipo']!=m['tipo']:raise ValueError('Material fora do corpus de integrais.')
    chunks=copy.deepcopy([c for c in dados['chunks'] if c['metadata']['arquivo']==origem['arquivo']])
    for c in chunks:
        meta=c['metadata'];a=assuntos[meta['assunto']]
        if not a['ativo'] or a['disciplina_id']!=m['disciplina_id']:raise ValueError('Assunto indisponível.')
        meta.update(material_id=m['id'],periodo_id=m['periodo_id'],disciplina_id=m['disciplina_id'],assunto_id=a['id'],
            fonte_monitor_virtual=m['fonte_monitor_virtual'],autorizacao_professor=m['autorizacao_professor'],disponivel_para_pratica=m['disponivel_para_pratica'])
    return chunks
