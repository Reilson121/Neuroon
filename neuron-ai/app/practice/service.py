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
        refs = repository.buscar_questoes(req["disciplina_id"], req.get("assunto_id"), req["material_ids"], req["origem"])
        for ref in refs:
            if not {f["material_id"] for f in ref["fontes"]}.issubset(set(req["material_ids"])):
                raise ValueError("Referência fora dos materiais elegíveis.")
        if req.get("assunto_id") is not None:
            refs = [r for r in refs if req["assunto_id"] in [r["assunto_id"], *r.get("assunto_ids", [])]]
        excluidos = set(req.get("excluir_fingerprints", []))
        if req["modo"] == "CADASTRADAS":
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
            questoes = []
            slugs = list(grupos); random.Random(secrets.randbits(128)).shuffle(slugs)
            cotas = {slug: 0 for slug in slugs}
            for i in range(req["quantidade"] if slugs else 0):
                cotas[slugs[i % len(slugs)]] += 1
            for slug in slugs:
                if cotas[slug]:
                    questoes.extend(self.gerador(slug, grupos[slug], cotas[slug], excluidos))
            if questoes:
                contextos = self.narrador(questoes)
                if len(contextos) != len(questoes):
                    raise ValueError("Contextos incompletos.")
                for q, contexto in zip(questoes, contextos):
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
