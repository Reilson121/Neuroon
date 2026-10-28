"""Importa somente os PDFs únicos e prepara corpus e catálogo reproduzíveis."""
import argparse
import json
import shutil
from pathlib import Path
from app.rag.sistemas_digitais_corpus import MATERIAIS, PASTA, JSON_CHUNKS, RAIZ, consolidar


def preparar(origem=None):
    PASTA.mkdir(parents=True, exist_ok=True)
    if origem:
        for _, nome in MATERIAIS:
            destino = PASTA / nome
            fonte = Path(origem) / nome
            if destino.exists() and destino.read_bytes() != fonte.read_bytes():
                raise ValueError(f'PDF diferente já existe: {nome}')
            if not destino.exists():
                shutil.copy2(fonte, destino)
    dados = consolidar()
    JSON_CHUNKS.parent.mkdir(parents=True, exist_ok=True)
    JSON_CHUNKS.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')
    sql = ["-- Sistemas Digitais: teoria disponível; lista e prova ainda não fornecidas.",
        "INSERT INTO periodo(numero,nome,ordem) VALUES(3,'3º período',3) ON CONFLICT(numero) DO NOTHING;",
        "INSERT INTO disciplina(periodo_id,nome,slug,descricao,possui_prova) SELECT id,'Sistemas Digitais','sistemas_digitais','Monitor e prática de IA com os materiais disponíveis. Lista e prova ainda não fornecidas.',TRUE FROM periodo WHERE numero=3 ON CONFLICT(slug) DO NOTHING;"]
    for ordem, a in enumerate(dados['arquivos'], 1):
        slug, titulo = a['assunto'], a['arquivo'][:-4]
        ref = 'local:' + a['pdf']
        sql += [f"INSERT INTO assunto(disciplina_id,nome,slug,ordem) SELECT id,'{titulo}','{slug}',{ordem} FROM disciplina WHERE slug='sistemas_digitais' ON CONFLICT(disciplina_id,slug) DO NOTHING;",
            f"INSERT INTO material(disciplina_id,assunto_id,titulo,descricao,tipo,referencia_externa,fonte_monitor_virtual) SELECT d.id,a.id,'{titulo}','PDF teórico; fonte de conceitos para Monitor e questões de IA.','SLIDE_AULA','{ref}',TRUE FROM disciplina d JOIN assunto a ON a.disciplina_id=d.id AND a.slug='{slug}' WHERE d.slug='sistemas_digitais' AND NOT EXISTS(SELECT 1 FROM material m WHERE m.disciplina_id=d.id AND m.referencia_externa='{ref}');"]
    migration = RAIZ.parent / 'backend/demo/src/main/resources/db/migration/V7__catalogo_sistemas_digitais.sql'
    migration.write_text('\n'.join(sql) + '\n', encoding='utf-8')
    print(json.dumps({k: dados[k] for k in ('disciplina', 'total_paginas', 'total_chunks')}, ensure_ascii=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--origem')
    preparar(parser.parse_args().origem)
