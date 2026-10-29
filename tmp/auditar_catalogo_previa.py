"""Auditoria somente leitura do catálogo e exportação dos metadados acadêmicos para QA."""
import json
import os
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / 'neuron-ai/.env')
load_dotenv(root / '.env')
with psycopg.connect(host=os.getenv('DB_HOST', 'localhost'), port=os.getenv('DB_PORT', '5432'),
                     dbname=os.getenv('DB_NAME', 'neuron'), user=os.getenv('DB_USER', 'postgres'),
                     password=os.getenv('DB_PASSWORD', ''), connect_timeout=5,
                     options='-c default_transaction_read_only=on', row_factory=dict_row) as con:
    periodos = con.execute('SELECT id,numero,nome FROM periodo WHERE ativo ORDER BY ordem').fetchall()
    disciplinas = con.execute('SELECT d.id,d.nome,d.descricao,d.possui_prova AS "possuiProva",d.periodo_id AS "periodoId",d.slug FROM disciplina d JOIN periodo p ON p.id=d.periodo_id WHERE d.ativo AND p.ativo ORDER BY d.nome').fetchall()
    assuntos = con.execute('SELECT a.id,a.nome,a.descricao,a.ordem,a.disciplina_id AS "disciplinaId" FROM assunto a JOIN disciplina d ON d.id=a.disciplina_id WHERE a.ativo AND d.ativo ORDER BY a.ordem,a.id').fetchall()
    materiais = con.execute('SELECT m.id,m.disciplina_id AS "disciplinaId",m.assunto_id AS "assuntoId",m.titulo,m.tipo,m.fonte_monitor_virtual AS "fonteMonitorVirtual",m.disponivel_para_pratica AS "disponivelParaPratica",m.contem_gabarito AS "contemGabarito",m.autorizacao_professor AS "autorizacaoProfessor",m.referencia_externa FROM material m JOIN disciplina d ON d.id=m.disciplina_id WHERE m.ativo AND d.ativo ORDER BY m.titulo').fetchall()
    historico = con.execute('SELECT version,success FROM flyway_schema_history WHERE version IS NOT NULL ORDER BY installed_rank').fetchall()
    chunks = con.execute('SELECT disciplina,count(*) AS total FROM chunk_documento GROUP BY disciplina ORDER BY disciplina').fetchall()
for m in materiais:
    ref = m.pop('referencia_externa') or ''
    m['arquivoDisponivel'] = False  # A prévia mostra metadados; não serve PDFs autenticados.
    m['arquivoLocalPresente'] = ref.startswith('local:materiais_academicos/') and (root / 'neuron-ai' / ref.removeprefix('local:')).is_file()
snapshot = dict(periodos=periodos, disciplinas=disciplinas, assuntos=assuntos, materiais=materiais)
(root / 'frontend/qa/catalogo.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(migrations=historico, catalogo=[dict(disciplina=d['nome'], periodo=d['periodoId'],
    assuntos=sum(a['disciplinaId'] == d['id'] for a in assuntos),
    materiais=sum(m['disciplinaId'] == d['id'] for m in materiais),
    arquivosPresentes=sum(m['disciplinaId'] == d['id'] and m['arquivoLocalPresente'] for m in materiais))
    for d in disciplinas], trechosIndexados=chunks), ensure_ascii=False, indent=2))
