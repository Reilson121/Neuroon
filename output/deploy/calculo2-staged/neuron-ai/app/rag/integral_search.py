"""Prioriza o apoio curricular; o complemento amplo exige pedido explícito."""
import re
import unicodedata

def ordenar_evidencias(candidatos,pergunta,k,assunto=None):
    texto=''.join(c for c in unicodedata.normalize('NFKD',pergunta.lower()) if not unicodedata.combining(c))
    opcional=assunto=='base_multivariavel' or re.search(r'varia(?:s|veis)|gradiente|lagrange|parciais|otimiz|complement|dominio|curvas de nivel|jacobiano|polares|cilindric|esferic',texto)
    # O índice relacional move assunto e período para colunas da linha.
    def meta(r):return {**r,**(r.get('metadata') or {})}
    if opcional:return candidatos[:k]
    curriculares=[r for r in candidatos if not meta(r).get('complementar') and meta(r).get('assunto')!='base_multivariavel']
    if re.search(r'(?:primeira|1[ªa]?) unidade|uma variavel|simples|indefinida|primitiva',texto):
        curriculares=[r for r in curriculares if meta(r).get('unidade')==1]
    elif 'dupla' in texto:curriculares=[r for r in curriculares if str(meta(r).get('assunto','')).startswith('integrais_duplas')]
    elif 'tripla' in texto:curriculares=[r for r in curriculares if str(meta(r).get('assunto','')).startswith('integrais_triplas')]
    return curriculares[:k]
