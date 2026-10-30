"""Copia os dez PDFs e prepara corpus e catálogo do segundo período."""
import argparse
import json
import shutil
from pathlib import Path
from app.rag.ed_basica_corpus import PASTA, RAIZ, JSON_CHUNKS, consolidar, MATERIAIS


def preparar(origem):
    PASTA.mkdir(parents=True,exist_ok=True)
    fontes=list(Path(origem).glob('UNIT_EDD_*.pdf'))+[Path(origem)/'prova_estrutura_de_dados_transcrita.pdf']
    if len(fontes)!=10:raise ValueError('Esperados nove materiais e uma prova parcial.')
    for fonte in fontes:
        destino=PASTA/fonte.name
        if destino.exists() and destino.read_bytes()!=fonte.read_bytes():raise ValueError('PDF existente diferente.')
        if not destino.exists():shutil.copy2(fonte,destino)
    dados=consolidar()
    JSON_CHUNKS.write_text(json.dumps(dados,ensure_ascii=False,indent=2),encoding='utf-8')
    def sql(s):return "'"+s.replace("'","''")+"'"
    linhas=["-- Estrutura de Dados do segundo período. Não altera a disciplina avançada do terceiro.",
        "INSERT INTO periodo(numero,nome,ordem) VALUES(2,'2º período',2) ON CONFLICT(numero) DO NOTHING;",
        "INSERT INTO disciplina(periodo_id,nome,slug,descricao,possui_prova) SELECT id,'Estrutura de Dados','estrutura_de_dados','C e estruturas básicas. UP1 parcial: quatro objetivas; duas abertas ausentes.',TRUE FROM periodo WHERE numero=2 ON CONFLICT(slug) DO NOTHING;"]
    for ordem,(slug,titulo) in enumerate(MATERIAIS,1):
        linhas.append(f"INSERT INTO assunto(disciplina_id,nome,slug,ordem) SELECT id,{sql(titulo)},{sql(slug)},{ordem} FROM disciplina WHERE slug='estrutura_de_dados' ON CONFLICT(disciplina_id,slug) DO NOTHING;")
    for a in dados['arquivos']:
        prova=a['tipo']=='PROVA_ANTIGA';ref='local:'+a['pdf']
        assunto='NULL' if prova else f"(SELECT id FROM assunto WHERE disciplina_id=d.id AND slug={sql(a['assunto'])})"
        linhas.append(f"INSERT INTO material(disciplina_id,assunto_id,titulo,descricao,tipo,referencia_externa,fonte_monitor_virtual,disponivel_para_pratica,autorizacao_professor) SELECT d.id,{assunto},{sql(a['titulo'])},{sql('Transcrição parcial; não contém as duas abertas nem gabarito oficial.' if prova else 'Material teórico para Monitor e geração de questões de estudo.')},{sql(a['tipo'])},{sql(ref)},TRUE,{'TRUE' if prova else 'FALSE'},{'TRUE' if prova else 'FALSE'} FROM disciplina d WHERE slug='estrutura_de_dados' AND NOT EXISTS(SELECT 1 FROM material m WHERE m.disciplina_id=d.id AND m.referencia_externa={sql(ref)});")
    alvo=RAIZ.parent/'backend/demo/src/main/resources/db/migration/V10__catalogo_estrutura_de_dados.sql'
    proposto='\n'.join(linhas)+'\n'
    if alvo.exists() and alvo.read_text(encoding='utf-8')!=proposto:raise ValueError('Migration existente diferente; crie uma nova versão.')
    alvo.write_text(proposto,encoding='utf-8')
    print(json.dumps(dict(pdfs=len(dados['arquivos']),paginas=dados['total_paginas'],chunks=dados['total_chunks']),ensure_ascii=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--origem',required=True);preparar(p.parse_args().origem)
