"""
Limpeza de texto extraído de PDFs exportados de apresentações.

Muitos slides exportados trazem o título duplicado (texto sobreposto),
por exemplo "Filas de / Prioridade" repetido 4 vezes seguidas. Isso
polui os embeddings e a busca.

Regras de segurança:
- só remove repetição CONSECUTIVA (blocos de 1 a 4 linhas);
- nunca mexe em blocos com linha indentada (provável código);
- ignora blocos sem texto de verdade (ex.: só "•" ou "}");
- só remove linhas, nunca altera nem reordena as que ficam.
"""

MAX_LINHAS_BLOCO = 4
MIN_LETRAS_BLOCO = 3


def _bloco_elegivel(bloco):
    """Bloco com texto real e sem indentação (não é código)."""
    if any(linha[:1].isspace() for linha in bloco):
        return False

    letras = sum(ch.isalpha() for linha in bloco for ch in linha)
    return letras >= MIN_LETRAS_BLOCO


def remover_repeticoes_consecutivas(texto):
    """
    Remove blocos de até 4 linhas repetidos em sequência, mantendo a
    primeira ocorrência. Compara ignorando espaços nas pontas.
    """
    linhas = texto.splitlines()
    mudou = True

    while mudou:
        mudou = False

        for tamanho in range(1, MAX_LINHAS_BLOCO + 1):
            i = 0

            while i + 2 * tamanho <= len(linhas):
                bloco = linhas[i:i + tamanho]
                seguinte = linhas[i + tamanho:i + 2 * tamanho]

                igual = (
                    [l.strip() for l in bloco]
                    == [l.strip() for l in seguinte]
                )

                if igual and _bloco_elegivel(bloco):
                    del linhas[i + tamanho:i + 2 * tamanho]
                    mudou = True
                else:
                    i += 1

    return "\n".join(linhas)
