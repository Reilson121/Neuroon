"""Percurso público Spring → contexto da conversa → IA, com conta descartável."""
import json
import secrets
from scripts.servicos_local import ambiente, AI
from scripts.validar_backend_estatistica import Cliente, hash_teste
from app.rag.vector_store import VectorStore


def main():
    env=ambiente();store=VectorStore();cliente=Cliente();uid=None
    relatorio={'aprovado':False,'turnos':[]}
    def perguntar(pergunta,disciplina,thread=None):
        csrf=cliente.chamar('GET','/api/v1/auth/csrf')
        r=cliente.http.post('/api/v1/monitor/chat',json={'pergunta':pergunta,
            'disciplinaId':disciplina,'threadId':thread},headers={csrf['headerName']:csrf['token']})
        r.raise_for_status();eventos={}
        for bloco in r.text.replace('\r\n','\n').split('\n\n'):
            linhas=bloco.splitlines();nome=next((l[6:].strip() for l in linhas if l.startswith('event:')),None)
            data='\n'.join(l[5:].strip() for l in linhas if l.startswith('data:'))
            if nome and data:eventos[nome]=json.loads(data)
        assert 'done' in eventos and 'error' not in eventos
        assert not eventos['done']['fallback'] and eventos['sources']['fontes']
        relatorio['turnos'].append({'pergunta':pergunta,'resposta':eventos['token']['texto'],'fontes':eventos['sources']['fontes']})
        return eventos['done']['threadId']
    try:
        senha=secrets.token_urlsafe(20);email='contexto-'+secrets.token_hex(8)+'@example.test'
        hashed=hash_teste(senha,env)
        with store._conectar() as c:
            uid=c.execute("INSERT INTO usuario(nome,email,senha_hash,perfil) VALUES('Teste contexto',%s,%s,'ESTUDANTE') RETURNING id",[email,hashed]).fetchone()[0]
            did=c.execute("SELECT id FROM disciplina WHERE slug='estrutura_de_dados_avancada'").fetchone()[0]
        cliente.login(email,senha)
        thread=perguntar('O que são pilhas?',did)
        assert perguntar('pode explicar de forma mais didática e visual?',did,thread)==thread
        assert '```' in relatorio['turnos'][-1]['resposta'] or '|' in relatorio['turnos'][-1]['resposta']
        detalhe=cliente.chamar('GET',f'/api/v1/monitor/conversas/{thread}')
        assert len(detalhe['mensagens'])==4 and detalhe['mensagens'][-1]['fontes']
        relatorio['aprovado']=True
        print('BACKEND PUBLICO: CONTINUIDADE, ESQUEMA E REABERTURA APROVADOS',flush=True)
    finally:
        cliente.close()
        if uid is not None:
            with store._conectar() as c:
                c.execute('DELETE FROM mensagem_monitor WHERE conversa_id IN (SELECT id FROM conversa_monitor WHERE usuario_id=%s)',[uid])
                c.execute('DELETE FROM conversa_monitor WHERE usuario_id=%s',[uid])
                c.execute('DELETE FROM usuario WHERE id=%s',[uid])
        relatorio['conta_temporaria_removida']=True
        (AI/'saidas_testes/validacao_backend_contexto.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
