"""Correções didáticas das questões objetivas efetivamente transcritas.

As respostas existentes na lista são usadas como referência, sem atribuir
oficialidade não confirmada. Cálculos abertos permanecem como referências;
não são convertidos silenciosamente em provas oficiais de múltipla escolha.
"""

EXPLICACOES = {
    1: ("Mediana", "Ordene os dados e encontre o centro.", "A mediana é o valor central dos dados ordenados. Se a quantidade é par, usa-se a média dos dois valores centrais.", "Não confunda mediana com moda, que é o valor mais frequente."),
    2: ("Amplitude", "R = máximo − mínimo", "A amplitude mede a distância entre o maior e o menor valor, não a diferença entre média e moda.", "Localize os dois extremos antes de subtrair."),
    3: ("Probabilidade condicional", "P(A|B) = P(A∩B)/P(B), com P(B)>0", "Condicionar em B significa restringir o espaço considerado aos resultados em que B ocorreu.", "Leia a barra vertical como 'sabendo que'."),
    4: ("Espaço amostral", "2 × 2 = 4 resultados ordenados", "As duas posições representam os resultados das duas moedas: CC, CK, KC e KK. CK e KC são resultados diferentes na descrição ordenada.", "Enumere cada etapa para não esquecer resultados possíveis."),
    5: ("Desvio-padrão", "σ = sqrt(Σ(x−μ)²/N), para população", "O desvio-padrão expressa a dispersão dos dados em torno da média e tem a mesma unidade dos dados originais.", "A variância usa quadrados; o desvio-padrão extrai a raiz da variância."),
    6: ("Covariância e associação linear", "cov(X,Y) = Σ[(xi−médiaX)(yi−médiaY)]/(n−1), para amostra", "O material indica a alternativa C. Ressalva de revisão por IA: a covariância depende da escala; dizer apenas 'próxima de zero' não basta, isoladamente, para concluir associação fraca. Covariância zero não garante independência.", "Diferencie associação linear, independência e efeito de escala."),
}


def preparar_original(q):
    if q.get("formato_original") != "multipla_escolha":
        return None
    numero = int(q["referencia_local"].rsplit("q", 1)[1])
    if numero not in EXPLICACOES:
        return None
    conceito, formula, resolucao, dica = EXPLICACOES[numero]
    material = q.get("gabarito_material")
    gabarito = material["alternativa"].upper() if material else {1:"B",2:"B",3:"A",4:"B",5:"B",6:"C"}[numero]
    if numero == 6 and not material:
        resolucao = resolucao.replace("O material indica a alternativa C.", "A revisão por IA considera C a resposta pretendida, com a ressalva a seguir.")
    aviso = "Explicação gerada por IA. O gabarito contido na lista tem autoria oficial não confirmada." if material else "Resolução gerada por IA; precisa ser conferida com o professor. Não há gabarito oficial identificado no material."
    if numero == 6:
        aviso += " Questão original com simplificação conceitual: a proximidade da covariância a zero depende da escala. Consulte a ressalva na resolução."
    return {
        "enunciado": q["enunciado"], "alternativas": {k.upper(): v for k, v in q["alternativas"].items()},
        "conceito": conceito, "gabarito": gabarito, "formula": formula,
        "substituicao": None, "calculos": [formula], "resolucao": resolucao,
        "erros_comuns": [dica], "dica": dica, "resolucao_gerada_por_ia": True,
        "origem_gabarito": "CONTIDO_NO_MATERIAL_AUTORIA_NAO_CONFIRMADA" if material else "GERADO_IA_NAO_OFICIAL",
        "aviso": aviso, "origem": "MATERIAL_ACADEMICO", "fontes": q["fontes"],
        "fingerprint": q["referencia_local"],
    }
