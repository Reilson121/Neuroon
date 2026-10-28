"""Validação real do RAG conversacional; não grava conversas de usuários."""
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx
from scripts.servicos_local import ambiente

CASOS = [
    ('estrutura_de_dados_avancada','revisao_estruturas_em_c','O que são pilhas?'),
    ('estatistica','medidas_de_tendencia_central','O que é média aritmética?'),
    ('design_de_artefatos_digitais','design_de_interface','O que é proximidade na Gestalt?'),
    ('projeto_de_ideacao_de_software','matriz_csd','O que é uma matriz CSD?'),
]


def main():
    ambiente()
    destino=Path(__file__).resolve().parents[1]/'saidas_testes/validacao_conversa_rag.json'
    report={'gerado_em_utc':datetime.now(timezone.utc).isoformat(),'disciplinas':[],'falhas':[],'aprovado':False}
    def salvar():
        destino.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    def conferir(condicao, mensagem, disciplina, pergunta):
        if not condicao:
            report['falhas'].append({'disciplina':disciplina,'pergunta':pergunta,'motivo':mensagem})
            salvar()
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=120,
                      headers={'X-Internal-Token':os.environ['NEURON_INTERNAL_TOKEN']}) as client:
        for tentativa in range(20):
            try:
                if client.get('/health',timeout=2).status_code==200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError('Aguarde a inicialização do serviço de IA antes da validação.')
        for disciplina,assunto,inicial in CASOS:
            historico=[]; caso={'disciplina':disciplina,'assunto':assunto,'turnos':[]}
            report['disciplinas'].append(caso)
            for pergunta in [inicial,'pode explicar de forma mais didática e visual?',
                             'Agora me dê outro exemplo simples, criado por você.',
                             'Qual é a capital da França?']:
                r=client.post('/internal/v1/chat',json={'pergunta':pergunta,'disciplina':disciplina,
                    'assunto':assunto,'historico':historico[-8:]})
                r.raise_for_status();resposta=r.json()
                caso['turnos'].append({'pergunta':pergunta,**resposta});salvar()
                print(disciplina,pergunta,'fallback='+str(resposta['fallback']),flush=True)
                if pergunta=='Qual é a capital da França?':
                    conferir(resposta['fallback'] and not resposta['fontes'], 'Pergunta independente herdou tema indevido.',disciplina,pergunta)
                else:
                    conferir(not resposta['fallback'] and resposta['fontes'], 'Continuação sem resposta fundamentada.',disciplina,pergunta)
                    conferir(all(f.get('disciplina')==disciplina and f.get('assunto')==assunto for f in resposta['fontes']), 'Fonte fora do contexto.',disciplina,pergunta)
                    if 'visual' in pergunta:
                        conferir('```' in resposta['resposta'] or '|' in resposta['resposta'], 'Pedido visual sem esquema/tabela.',disciplina,pergunta)
                    if 'criado por você' in pergunta:
                        conferir(bool(re.search(r'(?:criad[oa]|elaborad[oa])\s+(?:pela\s+)?IA\b',resposta['resposta'],re.I)), 'Exemplo sem identificação da IA.',disciplina,pergunta)
                historico.extend([{'papel':'USUARIO','conteudo':pergunta[:2000]},
                                  {'papel':'MONITOR','conteudo':resposta['resposta'][:2000]}])
    report['aprovado']=not report['falhas'];salvar()
    assert report['aprovado'], 'Confira os cenários não aprovados no relatório.'
    print('QUATRO DISCIPLINAS: CONVERSA, VISUAL, EXEMPLO E MUDANCA DE TEMA APROVADOS',flush=True)


if __name__=='__main__':main()
