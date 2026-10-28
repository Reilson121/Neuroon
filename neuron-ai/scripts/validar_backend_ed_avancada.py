"""Aceitação local: conta temporária, catálogo, PDFs, RAG e histórico.

--com-provedor faz uma pergunta acadêmica real ao modelo configurado.
Remove a conta e seu histórico ao encerrar. Não executar em produção.
"""
import argparse
import json
import os
import secrets
import uuid
from datetime import datetime, timezone
from scripts.servicos_local import ambiente, AI
from scripts.validar_backend_estatistica import Cliente, hash_teste
from app.rag.vector_store import VectorStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--com-provedor', action='store_true')
    args = parser.parse_args()
    env = ambiente()
    # A validação usa o mesmo modelo local já instalado para o serviço.
    os.environ.setdefault('HF_HUB_OFFLINE', env['HF_HUB_OFFLINE'])
    os.environ.setdefault('TRANSFORMERS_OFFLINE', env['TRANSFORMERS_OFFLINE'])
    store = VectorStore()
    cliente = Cliente()
    uid = None
    checks = []
    report = {'gerado_em_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks, 'aprovado': False}
    def ok(nome):
        checks.append(nome)
        print(nome+': OK', flush=True)
    try:
        cliente.chamar('GET', '/api/v1/periodos', status=401)
        senha = secrets.token_urlsafe(24)
        email = f'ed-{uuid.uuid4().hex}@example.test'
        senha_hash = hash_teste(senha, env)
        with store._conectar() as c:
            uid = c.execute("""INSERT INTO usuario(nome,email,senha_hash,perfil)
                VALUES('Aceitação ED',%s,%s,'ESTUDANTE') RETURNING id""", [email, senha_hash]).fetchone()[0]
        cliente.login(email, senha)
        periodos = cliente.chamar('GET', '/api/v1/periodos')
        periodo = next(p for p in periodos if p['numero'] == 3)
        disciplinas = cliente.chamar('GET', f"/api/v1/periodos/{periodo['id']}/disciplinas")
        ed = next(d for d in disciplinas if d['nome'] == 'Estrutura de Dados Avançada')
        assuntos = cliente.chamar('GET', f"/api/v1/disciplinas/{ed['id']}/assuntos")
        materiais = cliente.chamar('GET', f"/api/v1/disciplinas/{ed['id']}/materiais")
        assert len(assuntos) == 14 and len(materiais) == 3
        assert all(m['fonteMonitorVirtual'] and m['arquivoDisponivel'] for m in materiais)
        assert not ed['possuiProva']
        ok('catalogo_14_assuntos_3_aulas')
        for m in materiais:
            r = cliente.http.get(f"/api/v1/materiais/{m['id']}/arquivo")
            assert r.status_code == 200 and r.content.startswith(b'%PDF')
            assert r.headers['cache-control'] == 'no-store'
        ok('abertura_dos_tres_pdfs_autenticada')
        cliente.chamar('POST', '/api/v1/pratica/sessoes', {'disciplinaId': ed['id'], 'quantidade': 1}, status=409)
        ok('pratica_sem_material_nao_inventa_questoes')
        from app.rag.retriever import Retriever
        retriever = Retriever(store=store)
        with store._conectar() as c:
            slugs = dict(c.execute('SELECT id,slug FROM assunto WHERE disciplina_id=%s', [ed['id']]).fetchall())
        for a in assuntos:
            encontrados = retriever.recuperar(a['nome'], 'estrutura_de_dados_avancada', slugs[a['id']])
            assert encontrados
            assert all(q['metadata']['disciplina_id'] == ed['id'] and q['metadata']['assunto_id'] == a['id']
                       and q['metadata']['material_id'] in {m['id'] for m in materiais} for q in encontrados)
        ok('rag_filtrado_nos_14_assuntos_com_ids_relacionais')
        if args.com_provedor:
            heap = next(a for a in assuntos if slugs[a['id']] == 'filas_de_prioridade_e_heap')
            csrf = cliente.chamar('GET', '/api/v1/auth/csrf')
            r = cliente.http.post('/api/v1/monitor/chat', json={'disciplinaId': ed['id'], 'assuntoId': heap['id'],
                'pergunta': 'O que é uma fila de prioridade e como ela se relaciona com heap?'},
                headers={csrf['headerName']: csrf['token']})
            assert r.status_code == 200
            eventos = {}
            for bloco in r.text.replace('\r\n', '\n').split('\n\n'):
                linhas = bloco.splitlines()
                nome = next((l[6:].strip() for l in linhas if l.startswith('event:')), None)
                data = '\n'.join(l[5:].strip() for l in linhas if l.startswith('data:'))
                if nome and data: eventos[nome] = json.loads(data)
            assert 'done' in eventos and 'error' not in eventos and eventos['sources']['fontes']
            assert not eventos['done']['fallback']
            assert all(f['disciplina_id'] == ed['id'] and f['assunto_id'] == heap['id']
                       and f['material_id'] in {m['id'] for m in materiais}
                       for f in eventos['sources']['fontes'])
            thread = eventos['done']['threadId']
            conversa = cliente.chamar('GET', f'/api/v1/monitor/conversas/{thread}')
            assert len(conversa['mensagens']) == 2
            assert conversa['mensagens'][1]['fontes']
            report['monitor'] = conversa['mensagens'][1]
            ok('monitor_real_com_fontes_sse_e_historico')
        report['aprovado'] = True
    finally:
        cliente.close()
        if uid is not None:
            with store._conectar() as c:
                c.execute('DELETE FROM mensagem_monitor WHERE conversa_id IN (SELECT id FROM conversa_monitor WHERE usuario_id=%s)', [uid])
                c.execute('DELETE FROM conversa_monitor WHERE usuario_id=%s', [uid])
                c.execute('DELETE FROM usuario WHERE id=%s', [uid])
        report['conta_temporaria_removida'] = True
        (AI/'saidas_testes/ed_avancada_validacao_backend.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


if __name__ == '__main__':
    main()
