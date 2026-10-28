"""Aceitação pela mesma origem do frontend; complementa os testes de renderização.

Recebe somente credenciais de uma conta descartável de teste via stdin (JSON).
Não salva senha, cookie, token nem conteúdo pessoal. Não altera permissões.
Exige Vite:5173, Spring:8080 e FastAPI:8000 já disponíveis.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import httpx


def main():
    conta = json.loads(sys.stdin.readline())
    if not conta['email'].startswith('frontend-estatistica-') or not conta['email'].endswith('@example.test'):
        raise ValueError('Utilize somente uma conta descartável desta validação.')
    checks = []
    report = {'gerado_em_utc': datetime.now(timezone.utc).isoformat(),
              'origem': 'http://127.0.0.1:5173', 'checks': checks,
              'aprovado': False, 'validacao_visual': False}
    arquivo = Path(__file__).resolve().parents[1] / 'saidas_testes/estatistica_validacao_proxy_frontend.json'
    arquivo.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    def registrar(nome):
        checks.append(nome)
        arquivo.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(nome + ': OK', flush=True)

    with httpx.Client(base_url=report['origem'], timeout=125) as http:
        csrf = None

        def chamar(method, path, body=None, status=200):
            nonlocal csrf
            headers = {}
            if method != 'GET':
                if csrf is None:
                    csrf = chamar('GET', '/api/v1/auth/csrf')
                headers[csrf['headerName']] = csrf['token']
            r = http.request(method, path, headers=headers, json=body)
            if r.status_code != status:
                raise AssertionError(f'{method} {path}: esperado {status}, recebido {r.status_code}')
            return r.json() if r.content else None

        home = http.get('/')
        assert home.status_code == 200 and '<div id="root">' in home.text
        registrar('interface_real_disponivel_sem_preview_ficticia')
        chamar('GET', '/api/v1/auth/me', status=401)
        chamar('POST', '/api/v1/auth/login', {'email': conta['email'], 'senha': conta['senha']})
        csrf = None
        assert chamar('GET', '/api/v1/auth/me')['perfil'] == 'ESTUDANTE'
        registrar('login_cookie_e_csrf_pela_origem_do_frontend')
        periodo = next(p for p in chamar('GET', '/api/v1/periodos') if p['numero'] == 3)
        disciplina = next(d for d in chamar('GET', f"/api/v1/periodos/{periodo['id']}/disciplinas") if d['nome'] == 'Estatística')
        did = disciplina['id']
        assuntos = chamar('GET', f'/api/v1/disciplinas/{did}/assuntos')
        materiais = chamar('GET', f'/api/v1/disciplinas/{did}/materiais')
        assert len(assuntos) == 31 and len(materiais) == 3
        registrar('catalogo_real_terceiro_periodo_31_assuntos_tres_materiais')
        s = chamar('POST', '/api/v1/pratica/sessoes', {'disciplinaId': did, 'modo': 'CADASTRADAS', 'origem': 'MISTO', 'quantidade': 10, 'revisarVistas': True}, status=201)
        assert len(s['questoes']) == 6
        assert all(q['origem'] == 'MATERIAL_ACADEMICO' and q['fontes'] for q in s['questoes'])
        assert all(not any(k in q for k in ['alternativaCorreta', 'resolucao', 'calculos']) for q in s['questoes'])
        registrar('seis_questoes_originais_com_fontes_e_sem_gabarito_antecipado')
        q = s['questoes'][0]
        body = {'questaoId': q['id'], 'alternativa': 'A'}
        path = f"/api/v1/pratica/sessoes/{s['sessaoId']}/respostas"
        correcao = chamar('POST', path, body)
        assert correcao['alternativaCorreta'] in 'ABCDE' and correcao['conceito'] and correcao['resolucao'] and correcao['dica']
        assert correcao['fontes'] and correcao['aviso'] and correcao['resolucaoGeradaPorIa']
        assert chamar('POST', path, body) == correcao
        registrar('correcao_didatica_identificada_e_reenvio_idempotente')
        poisson = next(a for a in assuntos if 'Poisson' in a['nome'])
        empty = chamar('POST', '/api/v1/pratica/sessoes', {'disciplinaId': did, 'assuntoId': poisson['id'], 'modo': 'CADASTRADAS', 'quantidade': 1})
        assert empty['estado'] == 'SEM_QUESTOES' and not empty['questoes']
        registrar('assunto_sem_avaliacoes_retorna_estado_vazio')
        central = next(a for a in assuntos if 'tendência central' in a['nome'].lower())
        dispersao = next(a for a in assuntos if 'dispersão e posição' in a['nome'].lower())
        g = chamar('POST', '/api/v1/pratica/sessoes', {'disciplinaId': did, 'assuntoId': dispersao['id'], 'modo': 'GERADAS_IA', 'quantidade': 1}, status=201)
        assert len(g['questoes']) == 1 and g['questoes'][0]['origem'] == 'GERADA_IA'
        q = g['questoes'][0]
        c = chamar('POST', f"/api/v1/pratica/sessoes/{g['sessaoId']}/respostas", {'questaoId': q['id'], 'alternativa': 'A'})
        assert c['origemGabarito'] == 'GERADO_IA_VALIDADO_MATEMATICAMENTE'
        assert c['formula'] and c['substituicao'] and c['calculos'] and c['dica']
        registrar('questao_inedita_real_com_calculos_validados')
        r = http.post('/api/v1/monitor/chat', headers={csrf['headerName']: csrf['token']},
                      json={'disciplinaId': did, 'assuntoId': central['id'], 'pergunta': 'O que representa a mediana e quando ela é preferível à média?'})
        assert r.status_code == 200 and 'text/event-stream' in r.headers['content-type']
        eventos = {}
        for bloco in r.text.replace('\r\n', '\n').split('\n\n'):
            linhas = bloco.splitlines()
            nome = next((l[6:].strip() for l in linhas if l.startswith('event:')), None)
            dados = '\n'.join(l[5:].strip() for l in linhas if l.startswith('data:'))
            if nome and dados:
                eventos[nome] = json.loads(dados)
        assert 'error' not in eventos and eventos['token']['texto'] and not eventos['done']['fallback']
        fontes = eventos['sources']['fontes']
        assert fontes and all(f['disciplina'] == 'estatistica' and f['pagina'] for f in fontes)
        thread = eventos['done']['threadId']
        detalhe = chamar('GET', f'/api/v1/monitor/conversas/{thread}')
        assert len(detalhe['mensagens']) == 2 and detalhe['mensagens'][-1]['fontes']
        registrar('monitor_real_com_referencias_e_reabertura_do_historico')
        chamar('POST', '/api/v1/auth/logout', status=204)
        chamar('GET', '/api/v1/auth/me', status=401)
        registrar('logout_invalida_acesso_pela_interface')
        report['aprovado'] = True
        arquivo.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
