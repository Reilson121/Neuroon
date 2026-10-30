"""Prepara os cinco arquivos recebidos sem alterar os originais."""
import argparse
import json
import shutil
from pathlib import Path
from app.rag.calculo_corpus import PASTA, RAIZ, JSON_CHUNKS, consolidar, ASSUNTOS


def preparar(origem):
    PASTA.mkdir(parents=True, exist_ok=True)
    arquivos = [p for p in Path(origem).glob('*.pdf') if p.name.startswith(('01 ', '02 ', '03 ', 'Tabela de Derivadas', 'prova_calculo_transcrita'))]
    if len(arquivos)!=5: raise ValueError('Esperados os cinco PDFs de Cálculo informados.')
    for fonte in arquivos:
        destino = PASTA/fonte.name
        if destino.exists() and destino.read_bytes()!=fonte.read_bytes(): raise ValueError('Arquivo existente diferente.')
        if not destino.exists(): shutil.copy2(fonte, destino)
    dados = consolidar()
    JSON_CHUNKS.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')
    from app.practice.calculo_engine import TOPICOS
    slugs=[a[0] for a in ASSUNTOS]
    opcoes=[dict(id=t,assunto=v[0],assuntoOrdem=slugs.index(v[0])+1,unidade=v[1],nome=v[2],tipos=v[3]) for t,v in TOPICOS.items()]
    (RAIZ.parent/'frontend/src/calculo-topicos.json').write_text(json.dumps(opcoes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def sql(s): return "'"+s.replace("'", "''")+"'"
    linhas = ["-- Cálculo para Computação I: 2º período; derivadas somente na unidade 2.",
        "INSERT INTO periodo(numero,nome,ordem) VALUES(2,'2º período',2) ON CONFLICT(numero) DO NOTHING;",
        "INSERT INTO disciplina(periodo_id,nome,slug,descricao,possui_prova) SELECT id,'Cálculo para Computação I','calculo_para_computacao_1','Unidade 1: funções e limites. Unidade 2: derivadas. Somente a prova da unidade 1 foi fornecida.',TRUE FROM periodo WHERE numero=2 ON CONFLICT(slug) DO NOTHING;"]
    for ordem, (slug, titulo, descricao) in enumerate(ASSUNTOS, 1):
        linhas.append(f"INSERT INTO assunto(disciplina_id,nome,slug,descricao,ordem) SELECT id,{sql(titulo)},{sql(slug)},{sql(descricao)},{ordem} FROM disciplina WHERE slug='calculo_para_computacao_1' ON CONFLICT(disciplina_id,slug) DO NOTHING;")
    for a in dados['arquivos']:
        ref = 'local:'+a['pdf']; prova = a['tipo']=='PROVA_ANTIGA'
        descricao = 'UP1 transcrita; questões abertas, sem gabarito oficial. UP2 não fornecida.' if prova else 'Material de estudo; consulte as páginas originais para fórmulas e gráficos.'
        linhas.append(f"INSERT INTO material(disciplina_id,titulo,descricao,tipo,referencia_externa,fonte_monitor_virtual,disponivel_para_pratica,autorizacao_professor) SELECT d.id,{sql(a['titulo'])},{sql(descricao)},{sql(a['tipo'])},{sql(ref)},TRUE,{'TRUE' if prova else 'FALSE'},{'TRUE' if prova else 'FALSE'} FROM disciplina d WHERE slug='calculo_para_computacao_1' AND NOT EXISTS(SELECT 1 FROM material m WHERE m.disciplina_id=d.id AND m.referencia_externa={sql(ref)});")
    migration = RAIZ.parent/'backend/demo/src/main/resources/db/migration/V11__catalogo_calculo.sql'
    texto = '\n'.join(linhas)+'\n'
    if migration.exists() and migration.read_text(encoding='utf-8')!=texto: raise ValueError('Migration já existe com conteúdo diferente.')
    migration.write_text(texto, encoding='utf-8')
    print(json.dumps(dict(pdfs=len(arquivos), paginas=dados['total_paginas'], chunks=dados['total_chunks'])))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--origem',required=True);preparar(p.parse_args().origem)
