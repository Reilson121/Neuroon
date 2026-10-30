"""Seleciona a seção da regra explicitamente pedida, preservando suas fontes."""
import re
import unicodedata


def ordenar_evidencias(candidatos,pergunta,k):
    texto=''.join(c for c in unicodedata.normalize('NFKD',pergunta.casefold()) if not unicodedata.combining(c))
    regras=[(r'regra (?:da |de )?cadeia',23,28),
            (r'regra (?:do |de )?produto',11,14),
            (r'regra (?:do |de )?quociente',11,14),
            (r'regra (?:da |de )?potencia',2,6)]
    intervalo=next(((inicio,fim) for padrao,inicio,fim in regras if re.search(padrao,texto)),None)
    if not intervalo:return candidatos[:k]
    inicio,fim=intervalo
    def corresponde(r):
        arquivo=r.get('arquivo') or r.get('metadata',{}).get('arquivo','')
        pagina=r.get('pagina') or r.get('metadata',{}).get('pagina',0)
        return arquivo.startswith('Tabela de Derivadas') and pagina==1 or arquivo.startswith('03 ') and inicio<=pagina<=fim
    relevantes=[r for r in candidatos if corresponde(r)]
    # Não completa o contexto com exercícios de outra seção para atingir k.
    return relevantes[:k] if relevantes else candidatos[:k]
