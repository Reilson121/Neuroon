"""Sessões efêmeras internas; gabaritos nunca saem antes da resposta."""

import copy
import random
import secrets
import threading
import time
import uuid
from app.practice.originals import preparar_original
from app.practice.generation import gerar, contextos_ia
from app.practice.repository import QuestionRepository
from app.practice.math_engine import verificar


class PracticeError(RuntimeError):
    def __init__(self, status, codigo, mensagem):
        super().__init__(mensagem)
        self.status, self.codigo, self.mensagem = status, codigo, mensagem


class PracticeService:
    def __init__(self, repository=None, gerador=gerar, narrador=contextos_ia, ttl=3600, capacidade=1000):
        self.repository = repository
        self.gerador = gerador
        self.narrador = narrador
        self.ttl, self.capacidade = ttl, capacidade
        self.sessoes = {}
        self.lock = threading.RLock()

    def montar_questoes(self, req):
        with self.lock:
            agora = time.monotonic()
            self.sessoes = {k: v for k, v in self.sessoes.items() if v["expira"] > agora}
            if req["sessao_id"] in self.sessoes:
                raise PracticeError(409, "SESSAO_EXISTENTE", "Esta sessão já foi iniciada.")
            if len(self.sessoes) >= self.capacidade:
                raise PracticeError(429, "LIMITE_SESSOES", "Aguarde antes de iniciar outra prática.")
        repository = self.repository or QuestionRepository()
        filtros = (req["disciplina_id"], req.get("assunto_id"), req["material_ids"], req["origem"])
        refs = repository.buscar_questoes(*filtros, usar_teoria=True) if req['modo']=='GERADAS_IA' else repository.buscar_questoes(*filtros)
        for ref in refs:
            if not {f["material_id"] for f in ref["fontes"]}.issubset(set(req["material_ids"])):
                raise ValueError("Referência fora dos materiais elegíveis.")
        if req.get("assunto_id") is not None:
            refs = [r for r in refs if req["assunto_id"] in [r["assunto_id"], *r.get("assunto_ids", [])]]
        if req.get('assunto_ids'):
            selecionados = set(req['assunto_ids'])
            disponiveis = {aid for r in refs for aid in [r['assunto_id'], *r.get('assunto_ids', [])]}
            if not selecionados.issubset(disponiveis):
                raise PracticeError(409, 'CONTEUDO_INDISPONIVEL', 'Um conteúdo selecionado está sem material disponível. Revise sua seleção.')
            if req['quantidade'] < len(selecionados):
                raise PracticeError(400, 'QUANTIDADE_INSUFICIENTE', 'Escolha ao menos uma questão por conteúdo selecionado.')
            refs = [r for r in refs if selecionados.intersection([r['assunto_id'], *r.get('assunto_ids', [])])]
        excluidos = set(req.get("excluir_fingerprints", []))
        if any(r.get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'} for r in refs):
            if refs[0]['disciplina_slug']=='calculo_para_computacao_2':
                from app.practice.integral_engine import TOPICOS
            else:
                from app.practice.calculo_engine import TOPICOS
            topico=req.get('topico_calculo','MISTO')
            if refs[0]['disciplina_slug']=='calculo_para_computacao_2' and not req.get('assunto_id') and not req.get('assunto_ids') and topico=='MISTO':
                refs=[r for r in refs if r['assunto_principal_proposto']!='base_multivariavel']
            if topico!='MISTO' and topico not in TOPICOS:
                raise PracticeError(400,'TOPICO_INVALIDO','Escolha um tópico de Cálculo disponível.')
            refs=[r for r in refs if any(v[0]==r['assunto_principal_proposto']
                and (not req.get('unidade_calculo') or v[1]==req['unidade_calculo'])
                and (topico=='MISTO' or t==topico)
                and (req.get('tipo_funcao','MISTO')=='MISTO' or req['tipo_funcao'] in v[3]) for t,v in TOPICOS.items())]
            if req.get('assunto_ids') and not set(req['assunto_ids']).issubset({r['assunto_id'] for r in refs}):
                raise PracticeError(409,'CONTEUDO_INDISPONIVEL','Um conteúdo selecionado não possui referência compatível com os filtros de Cálculo.')
        if req["modo"] == "CADASTRADAS":
            refs = [r for r in refs if not r.get('referencia_teorica')]
            questoes = [q for r in refs if (q := preparar_original(r)) is not None and q["fingerprint"] not in excluidos]
            random.Random(secrets.randbits(128)).shuffle(questoes)
            questoes = questoes[:req["quantidade"]]
        else:
            # Agrupar por assunto evita gerar um tema sem questão de referência.
            grupos = {}
            for r in refs:
                slug = r["assunto_principal_proposto"]
                if req.get("assunto_id") is not None:
                    slug = r.get("assuntos_por_id", {}).get(str(req["assunto_id"]), slug if r["assunto_id"] == req["assunto_id"] else None)
                if slug is None:
                    continue
                grupos.setdefault(slug, []).append(r)
            if any(r.get('disciplina_slug') == 'estrutura_de_dados_avancada' for r in refs):
                from app.practice.ed_avancada_engine import CONCEITOS
                grupos = {s: rs for s, rs in grupos.items() if s in CONCEITOS}
            if any(r.get('disciplina_slug') == 'design_de_artefatos_digitais' for r in refs):
                from app.practice.design_bank import BANCOS
                grupos = {s: rs for s, rs in grupos.items() if s in BANCOS}
                disponiveis = {r['assunto_id'] for rs in grupos.values() for r in rs}
                if req.get('assunto_ids') and not set(req['assunto_ids']).issubset(disponiveis):
                    raise PracticeError(409, 'CONTEUDO_INDISPONIVEL', 'Um conteúdo selecionado está sem material disponível. Revise sua seleção.')
                if req.get('assunto_ids') and req['quantidade'] < len(req['assunto_ids']):
                    raise PracticeError(400, 'QUANTIDADE_INSUFICIENTE', 'Escolha ao menos uma questão por conteúdo selecionado.')
            questoes = []
            slugs = list(grupos); random.Random(secrets.randbits(128)).shuffle(slugs)
            cotas = {slug: 0 for slug in slugs}
            for i in range(req["quantidade"] if slugs else 0):
                cotas[slugs[i % len(slugs)]] += 1
            for indice_slug, slug in enumerate(slugs):
                if cotas[slug]:
                    if grupos[slug][0].get('disciplina_slug') == 'estrutura_de_dados_avancada':
                        from app.practice.ed_avancada_engine import gerar as gerar_avancada
                        tipo_avancada = req.get('tipo_questao', 'MISTO')
                        if tipo_avancada == 'MISTO' and len(slugs) > 1:
                            tipo_avancada = ['CONCEITUAL', 'TESTE_MESA'][indice_slug % 2]
                        questoes.extend(gerar_avancada(slug, grupos[slug], cotas[slug], excluidos,
                            tipo=tipo_avancada, nivel=req.get('nivel_contexto', 'DETALHADO')))
                    elif grupos[slug][0].get('disciplina_slug') == 'design_de_artefatos_digitais':
                        from app.practice.design_engine import gerar as gerar_design
                        questoes.extend(gerar_design(slug, grupos[slug], cotas[slug], excluidos))
                    elif grupos[slug][0].get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'}:
                        if grupos[slug][0]['disciplina_slug']=='calculo_para_computacao_2':
                            from app.practice.integral_engine import gerar as gerar_calculo
                        else:
                            from app.practice.calculo_engine import gerar as gerar_calculo
                        questoes.extend(gerar_calculo(slug,grupos[slug],cotas[slug],excluidos,
                            unidade=req.get('unidade_calculo',0),topico=req.get('topico_calculo','MISTO'),tipo_funcao=req.get('tipo_funcao','MISTO')))
                    elif grupos[slug][0].get('disciplina_slug') == 'estrutura_de_dados':
                        from app.practice.ed_basica_engine import gerar as gerar_ed
                        tipo=req.get('tipo_questao','MISTO')
                        if tipo=='MISTO' and len(slugs)>1:
                            tipo=['CONCEITUAL','TESTE_MESA','LOGICA','ESTILO_PROFESSOR'][indice_slug%4]
                        questoes.extend(gerar_ed(slug, grupos[slug], cotas[slug], excluidos,
                            tipo=tipo, nivel='DIRETO'))
                    else:
                        questoes.extend(self.gerador(slug, grupos[slug], cotas[slug], excluidos))
            if req.get('assunto_ids') and any(r.get('disciplina_slug') in {'calculo_para_computacao_1','calculo_para_computacao_2'} for r in refs):
                cobertos={r['assunto_id'] for q in questoes for r in grupos[TOPICOS[q['spec']['topico']][0]]}
                if len(questoes)!=req['quantidade'] or not set(req['assunto_ids']).issubset(cobertos):
                    raise PracticeError(409,'CONTEUDO_INDISPONIVEL','Não foi possível montar a prova completa com todos os conteúdos selecionados.')
                random.Random(secrets.randbits(128)).shuffle(questoes)
            basicas=[q for q in questoes if q.get('spec', {}).get('motor')=='estrutura_de_dados']
            if basicas:
                from app.practice.ed_basica_engine import contextualizar
                contextualizar(basicas,req.get('nivel_contexto','COTIDIANO'))
            # Redistribui cotas quando um conteúdo esgota suas questões inéditas.
            if any(r.get('disciplina_slug') == 'design_de_artefatos_digitais' for r in refs):
                for slug in slugs:
                    if len(questoes) >= req['quantidade']: break
                    questoes.extend(gerar_design(slug, grupos[slug], req['quantidade'] - len(questoes),
                        excluidos | {q['fingerprint'] for q in questoes}))
                if req.get('assunto_ids'):
                    cobertos = {r['assunto_id'] for q in questoes for r in grupos[q['spec']['assunto']]}
                    if not set(req['assunto_ids']).issubset(cobertos):
                        # Não iniciar uma prova que omita silenciosamente um conteúdo escolhido.
                        questoes = []
                random.Random(secrets.randbits(128)).shuffle(questoes)
            narraveis = [q for q in questoes if q.get('spec', {}).get('motor') not in {'calculo','integral','sistemas_digitais','estrutura_de_dados','estrutura_de_dados_avancada','design_de_artefatos_digitais'}]
            if narraveis:
                contextos = self.narrador(narraveis)
                if len(contextos) != len(narraveis):
                    raise ValueError("Contextos incompletos.")
                for q, contexto in zip(narraveis, contextos):
                    q["enunciado"] = contexto + "\n\n" + q["enunciado"]
        publicas = []
        segredos = {}
        for q in questoes:
            if q["origem"] == "GERADA_IA": verificar(q)
            qid = str(uuid.uuid4())
            q["id"] = qid
            q["disciplina_id"] = req["disciplina_id"]
            q["assunto_id"] = req.get("assunto_id")
            segredos[qid] = q
            publicas.append({k: q[k] for k in ["id", "enunciado", "alternativas", "conceito", "origem", "fontes", "aviso", "fingerprint", "disciplina_id", "assunto_id"]})
            if q.get("visualizacao"):
                publicas[-1]["visualizacao"] = q["visualizacao"]
        if segredos:
            with self.lock:
                if len(self.sessoes) >= self.capacidade:
                    raise PracticeError(429, "LIMITE_SESSOES", "Aguarde antes de iniciar outra prática.")
                self.sessoes[req["sessao_id"]] = {"usuario_id": req["usuario_id"], "expira": time.monotonic()+self.ttl,
                                                 "questoes": segredos, "respostas": {}}
        return {"questoes": publicas}

    def corrigir(self, req):
        with self.lock:
            s = self.sessoes.get(req["sessao_id"])
            if s is None or s["expira"] <= time.monotonic() or s["usuario_id"] != req["usuario_id"]:
                raise PracticeError(404, "SESSAO_NAO_ENCONTRADA", "Sessão expirada ou indisponível.")
            q = s["questoes"].get(req["questao_id"])
            if q is None:
                raise PracticeError(404, "QUESTAO_NAO_ENCONTRADA", "Questão não pertence à sessão.")
            if not {f["material_id"] for f in q["fontes"]}.issubset(set(req["material_ids"])):
                raise PracticeError(409, "MATERIAL_INDISPONIVEL", "Material não está mais disponível.")
            anterior = s["respostas"].get(q["id"])
            if anterior:
                if anterior[0] != req["alternativa"]:
                    raise PracticeError(409, "RESPOSTA_JA_REGISTRADA", "Esta questão já foi respondida.")
                return copy.deepcopy(anterior[1])
            if q["origem"] == "GERADA_IA": verificar(q)
            correcao = {"correto": req["alternativa"] == q["gabarito"], "alternativa_correta": q["gabarito"],
                        **{k: q[k] for k in ["conceito", "formula", "substituicao", "calculos", "resolucao", "erros_comuns", "dica", "resolucao_gerada_por_ia", "origem_gabarito", "aviso", "fontes"]}}
            s["respostas"][q["id"]] = (req["alternativa"], copy.deepcopy(correcao))
            return correcao
