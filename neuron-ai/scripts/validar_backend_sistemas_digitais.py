"""Aceitação HTTP local com conta temporária; não consulta o provedor pago."""
import json
import secrets
import uuid
from scripts.servicos_local import ambiente, ROOT
from scripts.validar_backend_estatistica import Cliente
from app.rag.vector_store import VectorStore


def main():
    ambiente()
    cliente = Cliente()
    store = VectorStore()
    email = 'validacao-digitais-' + uuid.uuid4().hex + '@example.test'
    senha = secrets.token_urlsafe(24)
    checks = []
    try:
        cliente.chamar('GET', '/api/v1/periodos', status=401)
        cliente.chamar('POST', '/api/v1/auth/cadastro',
                       dict(nome='Validação temporária Sistemas Digitais', email=email, senha=senha), status=201)
        assert cliente.login(email, senha)['perfil'] == 'ESTUDANTE'
        periodos = cliente.chamar('GET', '/api/v1/periodos')
        segundo = next(p for p in periodos if p['numero'] == 2)
        terceiro = next(p for p in periodos if p['numero'] == 3)
        ds = cliente.chamar('GET', f"/api/v1/periodos/{segundo['id']}/disciplinas")
        digital = next(d for d in ds if d['nome'] == 'Sistemas Digitais')
        assert digital['periodoId'] == segundo['id']
        assert all(d['nome'] != 'Sistemas Digitais' for d in
                   cliente.chamar('GET', f"/api/v1/periodos/{terceiro['id']}/disciplinas"))
        checks.append('Sistemas Digitais somente no segundo período pela API')
        did = digital['id']
        assuntos = cliente.chamar('GET', f'/api/v1/disciplinas/{did}/assuntos')
        materiais = cliente.chamar('GET', f'/api/v1/disciplinas/{did}/materiais')
        assert len(assuntos) == len(materiais) == 12
        assert all(m['fonteMonitorVirtual'] and m['arquivoDisponivel'] for m in materiais)
        for m in materiais:
            r = cliente.http.get(f"/api/v1/materiais/{m['id']}/arquivo")
            assert r.status_code == 200 and r.content.startswith(b'%PDF')
        checks.append('12 assuntos e abertura autenticada dos 12 PDFs')
        with store._conectar() as c:
            c.execute('SET TRANSACTION READ ONLY')
            total, corretos = c.execute("""SELECT count(*),count(*) FILTER
                (WHERE periodo='02' AND periodo_id=%s AND disciplina_id=%s)
                FROM chunk_documento WHERE disciplina='sistemas_digitais'""", [segundo['id'], did]).fetchone()
        assert total == corretos == 353
        checks.append('353 trechos vinculados ao segundo período')
        sessao = cliente.chamar('POST', '/api/v1/pratica/sessoes',
            dict(disciplinaId=did, assuntoId=assuntos[0]['id'], modo='GERADAS_IA', origem='MISTO', quantidade=1), status=201)
        assert sessao['questoes'] and all('gabarito' not in q for q in sessao['questoes'])
        checks.append('Prática real: interface pública → Spring → serviço de IA → banco')
        cliente.chamar('POST', '/api/v1/auth/logout', status=204)
    finally:
        cliente.close()
        with store._conectar() as c:
            c.execute('DELETE FROM usuario WHERE email=%s AND nome=%s',
                      [email, 'Validação temporária Sistemas Digitais'])
    relatorio = dict(aprovado=True, periodo=2, assuntos=12, pdfs=12, trechos=353,
                     checks=checks, conta_temporaria_removida=True, provedor_pago_utilizado=False)
    (ROOT / 'output/verificacao-sistemas-digitais.json').write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(relatorio, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
