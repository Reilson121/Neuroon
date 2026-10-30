"""Testes de mesa reproduzíveis: árvores, heap, ordenação, grafos e revisão."""
import heapq
from collections import deque
from app.practice import curated_engine as base

# Conceito, cenário, requisito, resposta, distratores, justificativa, âncoras.
CONCEITOS = {
 'revisao_estruturas_em_c': ('Pilha encadeada', 'Um editor precisa desfazer a alteração mais recente sem percorrer todo o histórico.', 'Qual estrutura e operação atendem diretamente a esse comportamento?', 'Pilha com remoção no topo.', ['Fila com remoção no início.', 'Vetor ordenado pelo texto das alterações.', 'Lista ordenada pela duração das alterações.', 'Árvore de busca pela data mais antiga.'], 'Desfazer a alteração mais recente requer retirar primeiro o último registro inserido; a pilha representa essa ordem.', ['pilha','lista']),
 'conceitos_de_arvores': ('Hierarquia e árvore', 'Uma organização representa setores subordinados em uma estrutura com uma raiz. Cada setor, exceto a raiz, tem exatamente um superior imediato.', 'Qual propriedade caracteriza essa representação como árvore enraizada?', 'Há um único caminho da raiz até cada setor e não há ciclos.', ['Todo setor precisa ter exatamente dois subordinados.', 'A raiz tem necessariamente grau zero.', 'Cada folha precisa apontar para a raiz, fechando um ciclo.', 'Todos os setores precisam estar no mesmo nível.'], 'A hierarquia de uma árvore é conexa e sem ciclos. O caminho da raiz a cada nó é único; o número de filhos pode variar.', ['árvore','arvore']),
 'arvores_em_python': ('Referências e nós em Python', 'Uma equipe representa categorias com a classe Node. Cada instância recebe uma lista children criada dentro de __init__, e duas variáveis podem apontar para o mesmo nó.', 'Qual afirmação descreve corretamente essa representação?', 'Alterar children por uma referência é visível por outra referência ao mesmo nó; instâncias distintas mantêm suas próprias listas.', ['Atribuir um nó a outra variável sempre clona toda a árvore.', 'Cada variável contém uma cópia independente do nó após uma atribuição simples.', 'Criar children dentro de __init__ faz todas as instâncias compartilharem uma única lista.', 'Objetos mutáveis não podem ser referenciados por mais de uma variável.'], 'A atribuição compartilha a referência ao objeto; não clona seus dados. Criar a lista no construtor fornece uma lista por instância.', ['children','referência','referencia']),
 'aplicacoes_de_arvores': ('Dependências hierárquicas', 'Um utilitário calcula o tamanho de cada pasta somando seus arquivos e o tamanho das subpastas. O tamanho de uma pasta depende dos resultados de suas filhas.', 'Qual estratégia permite calcular cada pasta depois de suas dependências?', 'Percorrer em pós-ordem, processando subpastas antes da pasta que as contém.', ['Processar apenas a raiz e ignorar subpastas.', 'Usar pré-ordem sem retornar aos resultados dos filhos.', 'Visitar as pastas em ordem alfabética, independentemente da hierarquia.', 'Somar somente o número de filhos imediatos.'], 'A pós-ordem resolve as subárvores antes do nó, disponibilizando os resultados necessários ao cálculo da pasta.', ['árvore','arvore']),
 'filas_de_prioridade_e_heap': ('Heap mínimo', 'Um agendador precisa retirar repetidamente a tarefa de menor prioridade numérica e recebe novas tarefas entre as retiradas.', 'Por que um heap mínimo é adequado?', 'Mantém o menor elemento na raiz e permite inserção e remoção do mínimo em O(log n).', ['Mantém o vetor inteiro em ordem crescente após qualquer inserção.', 'Garante busca de qualquer tarefa por identificador em O(1).', 'Mantém sempre o maior elemento na raiz.', 'Permite remover qualquer posição sem restaurar sua propriedade.'], 'A propriedade de heap garante a ordem entre pais e filhos, disponibiliza o mínimo na raiz e admite restauração ao longo de uma altura logarítmica.', ['heap']),
 'arvores_binarias_de_busca': ('ABB e ordem de inserção', 'Um sistema insere identificadores crescentes em uma árvore binária de busca comum, sem balanceamento. A equipe prevê crescimento do cadastro.', 'Qual risco deve considerar?', 'A árvore pode se tornar uma cadeia e a busca pode custar O(n).', ['Qualquer ABB mantém altura O(log n), independentemente das inserções.', 'Identificadores crescentes impedem qualquer inserção válida.', 'A busca passa a ter custo O(1) para todas as chaves.', 'Toda inserção reorganiza automaticamente a árvore como AVL.'], 'Sem balanceamento, inserções ordenadas podem produzir um único ramo de altura proporcional ao número de nós.', ['busca','binária','binaria']),
 'arvores_de_decisao': ('Caminho de decisão', 'Um serviço representa regras de encaminhamento por perguntas em nós internos e resultados nas folhas. Cada atendimento segue apenas as respostas compatíveis com seus dados.', 'Como obter o resultado de um atendimento?', 'Partir da raiz, avaliar a condição em cada nó visitado e seguir o ramo correspondente até uma folha.', ['Percorrer todas as folhas e escolher a de maior profundidade.', 'Ordenar alfabeticamente as condições antes de avaliar o caso.', 'Escolher a folha mais próxima sem avaliar as condições.', 'Visitar necessariamente todos os ramos para qualquer caso.'], 'A classificação segue o caminho definido pelas condições do caso, e o resultado fica na folha alcançada.', ['decisão','decisao']),
 'arvore_trie': ('Busca por prefixo', 'Um catálogo de termos deve sugerir palavras que começam com os caracteres já digitados. Muitos termos compartilham o mesmo início.', 'Qual característica de uma trie favorece essa tarefa?', 'Compartilhar caminhos de caracteres e localizar a subárvore associada ao prefixo.', ['Comparar apenas os comprimentos das palavras, ignorando seus caracteres.', 'Manter obrigatoriamente uma árvore binária balanceada de palavras inteiras.', 'Ordenar termos somente pela frequência, sem registrar caracteres.', 'Eliminar marcadores de fim e considerar todo prefixo uma palavra cadastrada.'], 'Na trie, caminhos comuns representam prefixos comuns. O marcador de término distingue palavras completas de prefixos que não são palavras cadastradas.', ['trie']),
 'arvores_balanceadas_e_avl': ('Balanceamento AVL', 'Um índice sofre inserções frequentes. A equipe usa uma AVL para evitar que o caminho de busca cresça como uma cadeia.', 'Qual condição deve ser restaurada depois de uma inserção?', 'Em cada nó, as alturas das subárvores esquerda e direita diferem no máximo em um.', ['Todos os nós devem ter exatamente dois filhos.', 'A raiz precisa conter a menor chave cadastrada.', 'Todas as folhas devem ficar obrigatoriamente na mesma profundidade.', 'A sequência de inserção deve ser mantida como um único ramo.'], 'A condição AVL limita o desbalanceamento local e mantém altura logarítmica. Rotações preservam a ordem da ABB ao restaurar esse equilíbrio.', ['avl']),
 'arvores_red_black': ('Invariantes red-black', 'Durante a revisão de um índice red-black, a equipe encontra um nó vermelho cujo pai também é vermelho. As chaves continuam respeitando a ordem de busca.', 'Qual diagnóstico é correto?', 'A ordem de busca não basta: a adjacência entre dois nós vermelhos viola uma invariante e exige correção.', ['A árvore é válida sempre que o percurso em ordem estiver ordenado.', 'Todo nó vermelho precisa necessariamente ter pai vermelho.', 'A violação pode ser ignorada porque a raiz não mudou.', 'A única correção possível é ordenar todas as chaves em um vetor.'], 'Além da ordem da ABB, a red-black usa invariantes de cor para limitar a altura, incluindo a proibição de pai e filho vermelhos.', ['red','negra','rubro']),
 'arvore_splay': ('Localidade e splay', 'Um catálogo consulta repetidamente os mesmos registros em intervalos curtos. A equipe considera uma splay para aproveitar esse padrão.', 'Como a estrutura se reorganiza após acessar uma chave existente?', 'Aplica rotações para trazer o nó acessado à raiz, favorecendo acessos posteriores a ele.', ['Garante que todos os acessos individuais tenham exatamente O(1).', 'Recolore nós para impor as invariantes red-black.', 'Impede mudanças na raiz depois da primeira inserção.', 'Remove a chave consultada após toda busca.'], 'O splaying move o nó acessado à raiz. O desempenho é analisado de forma amortizada; um acesso isolado ainda pode ser linear.', ['splay']),
 'algoritmos_de_ordenacao': ('Estabilidade de ordenação', 'Uma lista de inscrições já está ordenada por horário. A equipe quer ordená-la por turma e preservar a ordem de chegada entre inscrições da mesma turma.', 'Qual requisito deve impor ao novo algoritmo de ordenação?', 'Estabilidade: registros com a mesma chave de turma preservam sua ordem relativa anterior.', ['Ordenar somente o primeiro registro de cada turma.', 'Trocar obrigatoriamente a ordem entre registros com chaves iguais.', 'Usar qualquer algoritmo, pois toda ordenação é estável.', 'Ignorar a turma e manter apenas a ordem de horários.'], 'Uma ordenação estável preserva a ordem relativa de chaves iguais, conservando a ordem de chegada dentro de cada turma.', ['ordenação','ordenacao']),
 'grafos': ('Busca em largura', 'Uma rede modela conexões como arestas sem pesos. É necessário encontrar o menor número de conexões entre um ponto inicial e os demais pontos alcançáveis.', 'Qual estratégia atende ao requisito?', 'Busca em largura com fila, explorando os vértices por distância em número de arestas.', ['Busca em profundidade garantindo sempre o menor número de arestas.', 'Ordenação alfabética dos vértices sem consultar as arestas.', 'Remoção das conexões para transformar a rede em um vetor.', 'Escolha do vértice de maior grau em todos os passos, sem registrar distâncias.'], 'A BFS explora primeiro distância zero, depois um, dois e assim por diante. Em grafos sem pesos, isso fornece o menor número de arestas.', ['grafo','largura'])
}


def sequencia(xs):
    return ' → '.join(map(str, xs)) or 'vazia'


def elaborar(spec):
    slug, familia = spec['assunto'], spec['familia']
    conceito, cenario, pergunta, certa, erradas, explicacao, ancoras = CONCEITOS[slug]
    if familia == 'CONCEITUAL':
        corpo = dict(enunciado=cenario+'\n\n'+pergunta, conceito=conceito, formula=None, substituicao=None,
                     calculos=['Identifique o requisito do cenário.', explicacao, 'Compare esse requisito com as propriedades das estruturas propostas.'],
                     resolucao=explicacao, erros_comuns=['Não confunda uma propriedade de ordenação com garantias de balanceamento ou de desempenho.'],
                     dica='Justifique a estrutura escolhida pela operação que o cenário exige.')
        return corpo, certa, erradas, ancoras
    a, b, c = spec['valores']  # chaves distintas e crescentes
    linhas = []
    if slug == 'revisao_estruturas_em_c':
        codigo=f'pilha = []\npilha.append({a})\npilha.append({b})\nx = pilha.pop()\npilha.append({c})\nprint(pilha)'
        resultado=[a,c]; estados=[[],[a],[a,b],[a],[a,c]]
        etapas=['Inicial',f'append({a})',f'append({b})','pop()',f'append({c})']
        linhas=list(zip(etapas,[sequencia(s) for s in estados]))
        cenario='Um editor registra códigos de alterações em uma pilha para permitir desfazer a alteração mais recente.'
        explicacao=f'A remoção retira {b}, que estava no topo; depois a inserção coloca {c} no topo.'
    elif slug == 'conceitos_de_arvores':
        codigo=f'Árvore enraizada: {a} tem filhos {b} e {c}.\n{b} tem um filho {c+1}, que tem um filho {c+2}.\nOs demais nós não têm filhos.\nAltura de uma folha = 0; altura de um nó = 1 + maior altura de seus filhos.'
        resultado=3; linhas=[(c+2,0),(c+1,1),(b,2),(c,0),(a,3)]
        cenario='Um serviço representa níveis de subordinação por uma árvore e mede o maior caminho da raiz até uma folha.'
        explicacao='O maior caminho contém quatro nós e três arestas. A convenção fornecida mede altura em arestas.'
    elif slug == 'arvores_em_python':
        codigo=f'class Node:\n    def __init__(self, data):\n        self.data = data\n        self.children = []\n\nraiz = Node({a})\noutra = raiz\nfolha = Node({b})\noutra.children.append(folha)\nfolha.data = {c}\nprint(raiz.children[0].data)'
        resultado=c;linhas=[('raiz e outra',f'Mesmo nó, data={a}'),('append',f'Um filho, data={b}'),('folha.data atualizado',f'Filho passa a {c}'),('Leitura pela raiz',c)]
        cenario='Uma interface organiza categorias em nós Python. Duas partes do programa mantêm referências para a mesma categoria e uma delas altera um filho.'
        explicacao='outra e raiz referenciam o mesmo nó. O filho inserido é o próprio objeto folha; atualizar folha.data altera o valor acessado pela raiz.'
    elif slug == 'aplicacoes_de_arvores':
        ordem='pós-ordem'
        codigo=f'Árvore binária: raiz {b}, filho esquerdo {a}, filho direito {c}. Ambos os filhos são folhas.\n'
        codigo+=('visitar(no):\n    se no existe:\n        emitir(no.chave)\n        visitar(no.esquerdo)\n        visitar(no.direito)' if ordem=='pré-ordem' else 'visitar(no):\n    se no existe:\n        visitar(no.esquerdo)\n        visitar(no.direito)\n        emitir(no.chave)')
        resultado=[b,a,c] if ordem=='pré-ordem' else [a,c,b]
        linhas=[(i+1,v,sequencia(resultado[:i+1])) for i,v in enumerate(resultado)]
        cenario='Um navegador de categorias registra os identificadores dos nós na ordem em que a rotina os emite.'
        explicacao=f'O percurso é {ordem}. Somente a instrução emitir acrescenta um identificador à saída.'
    elif slug == 'filas_de_prioridade_e_heap':
        codigo=f'Heap mínimo vazio. Chaves menores saem primeiro.\nInserir {c}, {a}, {b}, nessa ordem.\nRemover o mínimo.\nInserir {a-1}.\nRemover o mínimo.\nRegistrar somente as duas chaves removidas.'
        heap=[]
        for v in [c,a,b]:
            heapq.heappush(heap,v);linhas.append((f'Inserir {v}',str(heap),'—'))
        x=heapq.heappop(heap);linhas.append(('Remover mínimo',str(heap),x))
        heapq.heappush(heap,a-1);linhas.append((f'Inserir {a-1}',str(heap),'—'))
        y=heapq.heappop(heap);linhas.append(('Remover mínimo',str(heap),y))
        resultado=[x,y];cenario='Um agendador representa tarefas por prioridades numéricas em um heap mínimo.'
        explicacao='A cada remoção, considere o menor elemento presente naquele momento, inclusive novas inserções.'
    elif slug == 'arvores_binarias_de_busca':
        codigo=f'ABB inicialmente vazia; chaves distintas.\nInserir {b}, {a}, {c}, nessa ordem.\nBuscar a chave {c}.\nA cada comparação, registrar a chave visitada; menor segue à esquerda, maior à direita.'
        raiz=None
        for valor in [b,a,c]:
            if raiz is None:raiz=[valor,None,None];continue
            no=raiz
            while True:
                lado=1 if valor<no[0] else 2
                if no[lado] is None:no[lado]=[valor,None,None];break
                no=no[lado]
        no=raiz;resultado=[]
        while no:
            resultado.append(no[0]);linhas.append((no[0],f'{c} comparado com {no[0]}'))
            if no[0]==c:break
            no=no[1 if c<no[0] else 2]
        cenario='Um cadastro indexa identificadores em uma ABB e precisa auditar o caminho de uma busca.'
        explicacao=f'A raiz é {b}. Como {c} é maior, a busca segue à direita e encontra {c}; {a} não é visitado.'
    elif slug == 'arvores_de_decisao':
        codigo=f'valor = {b}\nse valor < {a}:\n    emitir("Rota A")\nsenão se valor <= {b}:\n    emitir("Rota B")\nsenão:\n    emitir("Rota C")'
        resultado='Rota B'
        linhas=[(f'{b} < {a}','falso'),(f'{b} <= {b}','verdadeiro'),('Folha','Rota B')]
        cenario='Um centro de distribuição usa regras de limite para encaminhar uma medida às rotas de atendimento.'
        explicacao='A primeira condição falha; a segunda inclui o valor de fronteira porque usa menor ou igual.'
    elif slug == 'arvore_trie':
        palavras=[f'sol{a}',f'sol{b}',f'som{c}',f'lar{a}']; prefixo='sol' if a%2 else 'so'
        codigo=f'Trie vazia. Inserir as palavras {palavras!r}.\nMarcar somente as palavras completas como terminais.\nConsultar o prefixo "{prefixo}".\nQuantas palavras completas cadastradas começam com esse prefixo?'
        resultado=sum(w.startswith(prefixo) for w in palavras)
        linhas=[(w,'sim' if w.startswith(prefixo) else 'não') for w in palavras]
        cenario='Um catálogo usa uma trie para sugerir termos a partir do início digitado pelo usuário.'
        explicacao='Conte os marcadores de palavras completas na subárvore do prefixo; não conte todos os nós como palavras.'
    elif slug in {'arvores_balanceadas_e_avl','arvores_red_black','arvore_splay'}:
        if slug=='arvores_balanceadas_e_avl':
            codigo=f'AVL vazia: inserir {a}, {b}, {c}, nessa ordem.\nFator de equilíbrio = altura(esquerda) - altura(direita).\nAltura de folha = 0; altura de subárvore vazia = -1.\nReequilibrar após cada inserção.\nQual será a raiz final?'
            linhas=[(f'Inserir {a}',str(a),'0'),(f'Inserir {b}',str(a),'-1'),(f'Inserir {c}',str(a),'-2'),('Rotação à esquerda',str(b),'0')]
            explicacao='A terceira inserção cria um caso direita-direita. A rotação simples à esquerda promove a chave intermediária.'
        elif slug=='arvores_red_black':
            codigo=f'Red-black vazia: inserir {a}, {b}, {c}, nessa ordem.\nUsar inserção de ABB, novo nó vermelho, folhas NIL pretas e raiz preta.\nNo conflito pai vermelho com tio preto, aplicar as rotações e recolorações usuais.\nQual será a chave da raiz final?'
            linhas=[(f'Inserir {a}',f'{a} preto'),(f'Inserir {b}',f'{a} preto; {b} vermelho'),(f'Inserir {c}','Pai vermelho, tio NIL preto'),('Rotação e recoloração',f'{b} preto; filhos {a} e {c} vermelhos')]
            explicacao='O conflito é externo à direita, com tio NIL preto. Rotacionar à esquerda e recolorir promove a chave intermediária e mantém a raiz preta.'
        else:
            codigo=f'Splay inicial: raiz {c}, filho esquerdo {b}; {b} tem filho esquerdo {a}.\nDemais filhos vazios. Buscar {a} e aplicar splaying até a raiz.\nCaso zig-zig à esquerda: rotacionar à direita no avô e depois à direita no pai.\nQual será a raiz final?'
            linhas=[('Inicial',str(c)),('Rotação à direita no avô',str(b)),('Rotação à direita no pai',str(a))]
            explicacao='O acesso segue dois ramos esquerdos. As duas rotações à direita trazem a chave acessada à raiz.'
        resultado=a if slug=='arvore_splay' else b
        cenario='Um índice de registros recebe operações e precisa manter suas regras de reorganização. As chaves representam identificadores únicos.'
    elif slug == 'algoritmos_de_ordenacao':
        valores=[c,a,b,a-1];atual=list(valores)
        codigo=f'v = {valores}\n# Uma única passagem de bubble sort, da esquerda para a direita\npara i de 0 até tamanho(v)-2, inclusive:\n    se v[i] > v[i+1]:\n        trocar v[i] e v[i+1]\nemitir(v)'
        for i in range(len(atual)-1):
            if atual[i]>atual[i+1]:atual[i],atual[i+1]=atual[i+1],atual[i]
            linhas.append((i,str(atual)))
        resultado=atual;cenario='Uma rotina de ordenação organiza prioridades. A equipe interrompe a execução após uma passagem para conferir o estado intermediário.'
        explicacao='Cada comparação usa o vetor já alterado pela comparação anterior. Uma passagem leva o maior ao fim, mas não necessariamente ordena todo o vetor.'
    else:
        adj={a:[b,c],b:[a,c+1],c:[a,c+1],c+1:[b,c]}
        codigo=f'Grafo não dirigido: adjacências {adj}.\nBFS a partir de {a}. Visitar vizinhos em ordem numérica crescente.\nMarcar um vértice ao enfileirar; nunca enfileirar um já marcado.\nRegistrar vértices quando forem retirados da fila.'
        fila=deque([a]);vistos={a};resultado=[]
        while fila:
            v=fila.popleft();resultado.append(v)
            for w in sorted(adj[v]):
                if w not in vistos:vistos.add(w);fila.append(w)
            linhas.append((v,sequencia(fila),sequencia(resultado)))
        cenario='Uma rede representa conexões entre unidades por um grafo. Uma busca deve registrar as unidades na ordem em que são processadas.'
        explicacao='A fila preserva a ordem de descoberta. Marcar ao enfileirar impede que o vértice compartilhado seja colocado na fila duas vezes.'

    if isinstance(resultado,list):
        certa=sequencia(resultado)
        candidatos=[sequencia(list(reversed(resultado))),sequencia([a,b,c]),sequencia([c,b,a]),
                    sequencia([a,c]),sequencia([b,c]),sequencia([c,a]),sequencia([a,b]),
                    *[sequencia([a,b,c,x]) for x in range(4)]]
    elif isinstance(resultado,int):
        certa=str(resultado);candidatos=[str(v) for v in [resultado-1,resultado+1,resultado+2,resultado+3,resultado+4] if v>=0]
    else:
        certa=resultado;candidatos=['Rota A','Rota C','Nenhuma rota','Todas as rotas']
    erradas=list(dict.fromkeys(v for v in candidatos if v!=certa))[:4]
    cabecalhos=['Etapa' if slug!='grafos' else 'Retirado']+['Estado '+str(i) for i in range(1,len(linhas[0]))]
    if slug=='conceitos_de_arvores':cabecalhos=['Nó','Altura em arestas']
    if slug=='revisao_estruturas_em_c':cabecalhos=['Operação','Pilha da base ao topo']
    if slug=='arvores_em_python':cabecalhos=['Etapa','Objeto observado']
    if slug=='arvores_binarias_de_busca':cabecalhos=['Chave visitada','Comparação']
    if slug=='arvores_de_decisao':cabecalhos=['Condição ou etapa','Resultado']
    if slug=='arvore_trie':cabecalhos=['Palavra cadastrada','Começa com o prefixo?']
    if slug=='arvores_balanceadas_e_avl':cabecalhos=['Operação','Raiz','Fator de equilíbrio na raiz']
    if slug=='arvores_red_black':cabecalhos=['Operação','Estrutura e cores']
    if slug=='arvore_splay':cabecalhos=['Etapa','Raiz']
    if slug=='grafos':cabecalhos=['Retirado','Fila após expansão','Saída acumulada']
    if slug=='filas_de_prioridade_e_heap':cabecalhos=['Operação','Heap em vetor','Chave removida']
    if slug=='aplicacoes_de_arvores':cabecalhos=['Emissão','Chave','Saída acumulada']
    if slug=='algoritmos_de_ordenacao':cabecalhos=['i','Vetor após comparação']
    comando='Faça o teste de mesa. Qual é o resultado solicitado ao final da execução?'
    if slug=='conceitos_de_arvores':comando='Faça o teste de mesa de baixo para cima. Qual é a altura da raiz?'
    if isinstance(resultado,list):comando+=' Nas alternativas, os valores da sequência aparecem separados por →.'
    texto='```text\n'+codigo+'\n```\n\n'+comando
    nivel=spec.get('nivel','DETALHADO')
    if nivel!='DIRETO':
        texto=cenario+(' Antes de usar a rotina em produção, a equipe quer conferir o resultado com uma execução manual. Considere exatamente a estrutura inicial e as regras descritas abaixo.' if nivel=='DETALHADO' else '')+'\n\n'+texto
    resolucao='### Teste de mesa resolvido\n\n'+base.tabela(cabecalhos,linhas)+'\n\n'+explicacao+'\n\nResultado: **'+certa+'**.'
    corpo=dict(enunciado=texto,conceito=conceito+' — teste de mesa',formula=None,substituicao=None,
               calculos=['Copie o estado inicial e identifique a ordem das operações.',explicacao,'Atualize o estado após cada operação; confira o resultado final: '+certa+'.'],
               resolucao=resolucao,erros_comuns=['Não use estados anteriores depois de uma alteração.','Diferencie o estado final, a sequência de visitas e os valores emitidos.'],
               dica='Monte as colunas no papel e registre cada alteração antes de conferir as alternativas.')
    return corpo,certa,erradas,ancoras


def verificar(q):
    return base.verificar(q,elaborar)


def gerar(slug,referencias,quantidade,excluidos,tipo='MISTO',nivel='DETALHADO'):
    if slug not in CONCEITOS:return []
    def specs(rng):
        tipos=['CONCEITUAL','TESTE_MESA'] if tipo=='MISTO' else [tipo]
        for i in range(quantidade*80):
            familia=tipos[i%len(tipos)]
            yield dict(motor='estrutura_de_dados_avancada',assunto=slug,
                       familia='CONCEITUAL' if familia=='CONCEITUAL' else 'TESTE_MESA',
                       **({} if familia=='CONCEITUAL' else dict(valores=sorted(rng.sample(range(10,90),3)))),nivel=nivel)
    return base.gerar_com_fontes(slug,referencias,quantidade,excluidos,specs,elaborar,'estrutura_de_dados_avancada')
