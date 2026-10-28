# Classe que representa um nó da árvore AVL
class NoAVL:
    def __init__(self, valor):
        self.valor = valor            # Valor armazenado no nó
        self.esquerda = None          # Referência para subárvore esquerda
        self.direita = None           # Referência para subárvore direita
        self.altura = 1               # Altura inicial do nó (1 = nó sozinho)

# Função que retorna a altura de um nó (ou 0 se for None)
def altura(no):
    if not no:
        return 0
    return no.altura

# Função que calcula o fator de balanceamento de um nó
def fator_balanceamento(no):
    if not no:
        return 0
    return altura(no.esquerda) - altura(no.direita)

# Rotação simples para a direita (caso esquerda-esquerda)
def rotacao_direita(y):
    x = y.esquerda
    T2 = x.direita

    # Rotaciona
    x.direita = y
    y.esquerda = T2

    # Atualiza alturas
    y.altura = 1 + max(altura(y.esquerda), altura(y.direita))
    x.altura = 1 + max(altura(x.esquerda), altura(x.direita))

    return x

# Rotação simples para a esquerda (caso direita-direita)
def rotacao_esquerda(x):
    y = x.direita
    T2 = y.esquerda

    # Rotaciona
    y.esquerda = x
    x.direita = T2

    # Atualiza alturas
    x.altura = 1 + max(altura(x.esquerda), altura(x.direita))
    y.altura = 1 + max(altura(y.esquerda), altura(y.direita))

    return y

# Função para inserir um valor na árvore AVL
def inserir(no, valor):
    # Passo 1: inserção normal como em uma árvore binária de busca
    if not no:
        return NoAVL(valor)
    elif valor < no.valor:
        no.esquerda = inserir(no.esquerda, valor)
    else:
        no.direita = inserir(no.direita, valor)

    # Passo 2: atualizar altura do nó atual
    no.altura = 1 + max(altura(no.esquerda), altura(no.direita))

    # Passo 3: verificar fator de balanceamento
    balanceamento = fator_balanceamento(no)

    # Caso 1: Esquerda Esquerda
    if balanceamento > 1 and valor < no.esquerda.valor:
        return rotacao_direita(no)

    # Caso 2: Direita Direita
    if balanceamento < -1 and valor > no.direita.valor:
        return rotacao_esquerda(no)

    # Caso 3: Esquerda Direita
    if balanceamento > 1 and valor > no.esquerda.valor:
        no.esquerda = rotacao_esquerda(no.esquerda)
        return rotacao_direita(no)

    # Caso 4: Direita Esquerda
    if balanceamento < -1 and valor < no.direita.valor:
        no.direita = rotacao_direita(no.direita)
        return rotacao_esquerda(no)

    return no  # Retorna o nó (sem mudanças se não precisou rotacionar)

# Função para imprimir a árvore em ordem (esquerda -> raiz -> direita)
def em_ordem(no):
    if no:
        em_ordem(no.esquerda)
        print(no.valor, end=" ")
        em_ordem(no.direita)

# Exemplo de uso:
raiz = None
valores = [30, 20, 10, 25, 40, 50, 22]
for v in valores:
    raiz = inserir(raiz, v)

print("Árvore AVL em ordem:")
em_ordem(raiz)
