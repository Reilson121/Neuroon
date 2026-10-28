"""Questões autorais de IA, revisadas conceitualmente; não são avaliações oficiais.

Cada registro contém conceito, âncoras para localizar a fonte, situação,
alternativa correta, distratores e roteiro que ensina a resolver.
"""

BANCOS = {}


def item(slug, chave, conceito, ancoras, enunciado, correta, erradas, passos, erro):
    BANCOS.setdefault(slug, []).append(dict(id=chave, conceito=conceito, ancoras=ancoras,
        enunciado=enunciado, correta=correta, erradas=erradas, passos=passos, erro=erro))


item('sistemas_analogicos_e_digitais', 'sinal', 'Sinais analógicos e digitais', ['analógico', 'digital'],
    'Um sensor acompanha continuamente a temperatura de uma sala. Para tratar sua informação em um sistema binário, como distinguir o sinal físico original de sua representação digital?',
    'O sinal analógico admite variação contínua; a representação digital usa níveis discretos.',
    ['O sinal analógico só admite zero e um.', 'O sinal digital assume todos os valores reais sem discretização.', 'Analógico e digital se distinguem apenas pela cor dos fios.', 'A representação digital elimina qualquer limitação de precisão.'],
    ['Identifique a grandeza física: a temperatura varia continuamente.', 'Compare os valores possíveis: um sistema digital representa a informação por estados discretos.', 'Relacione contínuo a analógico e discreto a digital; não confunda representação com precisão ilimitada.'],
    'Digital não significa precisão infinita; a informação é representada em níveis discretos.')
item('sistemas_analogicos_e_digitais', 'variavel', 'Variáveis booleanas', ['variáveis', 'lógicos'],
    'Um controlador representa a presença de uma peça por P=1 e sua ausência por P=0. Qual interpretação está correta?',
    'P é uma variável booleana com dois estados lógicos definidos pelo projeto.',
    ['P deve assumir qualquer valor real entre zero e um.', 'P é uma medida contínua da massa da peça.', 'O valor lógico um significa sempre exatamente um volt.', 'P não pode ser usado como entrada de uma porta lógica.'],
    ['Leia o significado atribuído a cada estado.', 'Observe que só existem duas possibilidades lógicas.', 'Classifique a variável como booleana, separando nível lógico de tensão elétrica exata.'],
    'Um estado lógico não fixa sozinho a tensão elétrica da implementação.')

item('portas_logicas_e_circuitos_digitais', 'and', 'Porta AND', ['and'],
    'Uma prensa só pode operar se a proteção estiver fechada (F=1) e o botão de partida estiver pressionado (P=1). Qual função atende ao requisito?',
    'S = F AND P.', ['S = F OR P.', 'S = NOT F.', 'S = F XOR P.', 'S é sempre um.'],
    ['Traduza cada condição para uma entrada booleana.', 'A expressão “e” exige simultaneidade: nenhuma entrada sozinha deve liberar a prensa.', 'Use AND; confira que 00, 01 e 10 bloqueiam, enquanto 11 libera.'],
    'OR liberaria a prensa quando apenas uma das condições estivesse satisfeita.')
item('portas_logicas_e_circuitos_digitais', 'xor', 'Porta XOR', ['xor'],
    'Um painel deve acender quando exatamente um de dois sensores estiver ativo. Qual porta representa essa condição?',
    'XOR, que produz um quando as entradas são diferentes.',
    ['OR, que produz zero quando ambas as entradas são um.', 'AND, que produz um quando as entradas são diferentes.', 'NOT, que compara diretamente duas entradas.', 'XNOR, que produz um apenas quando as entradas são diferentes.'],
    ['Liste os casos desejados: 01 e 10.', 'Exclua 00 e 11 porque não têm exatamente uma entrada ativa.', 'Reconheça a operação OU exclusivo: XOR.'],
    'OR inclusivo também aceita 11; XOR não aceita esse caso.')

item('algebra_booleana', 'demorgan', 'Teorema de De Morgan', ['morgan'],
    'Um alarme foi especificado por NOT(A AND B). Uma equipe quer montar uma expressão equivalente usando OR. Qual é a transformação correta?',
    '(NOT A) OR (NOT B).', ['(NOT A) AND (NOT B).', 'A OR B.', 'A AND B.', 'NOT(A OR B).'],
    ['Identifique a negação aplicada ao produto lógico inteiro.', 'Aplique De Morgan: negue cada variável e troque AND por OR.', 'Confira A=B=1: a expressão original e a transformada produzem zero.'],
    'Negar as entradas sem trocar o operador não é a aplicação de De Morgan.')
item('algebra_booleana', 'karnaugh', 'Mapa de Karnaugh', ['karnaugh'],
    'Ao simplificar uma função, uma equipe procura reunir células adjacentes com saída um em um mapa de Karnaugh. Qual procedimento é adequado?',
    'Formar grupos de tamanho potência de dois, respeitando a adjacência do mapa.',
    ['Formar qualquer grupo de três células.', 'Tratar apenas a diagonal como adjacência.', 'Alterar a saída de células para aumentar os grupos.', 'Ordenar as linhas por qualquer permutação sem preservar a adjacência.'],
    ['Monte o mapa com a ordenação que preserva a mudança de um bit entre vizinhos.', 'Localize os uns que podem ser agrupados em blocos de 1, 2, 4, 8 e assim por diante.', 'Mantenha apenas as variáveis constantes em cada grupo para construir a expressão simplificada.'],
    'Células diagonais não são vizinhas apenas por estarem próximas visualmente.')

item('circuitos_logicos', 'serie', 'Chaves em série', ['série'],
    'Duas chaves ideais normalmente abertas estão em série com uma lâmpada. Adote um para chave fechada. Qual situação permite a passagem de corrente pelo caminho completo?',
    'As duas chaves fechadas, comportamento equivalente a AND.',
    ['Apenas a primeira fechada, comportamento AND.', 'Qualquer uma fechada, comportamento OR.', 'As duas abertas, comportamento AND.', 'Somente as chaves em estados diferentes, comportamento XNOR.'],
    ['Siga o único caminho da corrente desde a fonte até a lâmpada.', 'Uma chave aberta interrompe todo o caminho em série.', 'Conclua que ambas devem fechar: a condição lógica é AND.'],
    'Não confunda a continuidade de um circuito em série com a de caminhos paralelos.')
item('circuitos_logicos', 'paralelo', 'Chaves em paralelo', ['paralelo'],
    'Dois botões normalmente abertos estão em paralelo, e qualquer um deve ligar uma campainha. Com um para botão fechado, qual operação descreve o acionamento?',
    'OR: basta um dos caminhos estar fechado.',
    ['AND: os dois caminhos precisam fechar sempre.', 'XOR: fechar ambos obrigatoriamente desliga a campainha.', 'NOT: a campainha só liga com todos os caminhos abertos.', 'A saída não depende dos botões.'],
    ['Identifique os caminhos alternativos até a campainha.', 'Teste 10 e 01: cada caso mantém um caminho condutor.', 'Teste 11: também conduz; a função é OR inclusivo.'],
    'A existência de dois caminhos fechados não cancela a condução.')

item('contadores', 'sincrono', 'Contadores síncronos e assíncronos', ['síncrono', 'assíncrono'],
    'Uma equipe compara um contador cujos flip-flops recebem o mesmo clock com outro em que a mudança de um estágio dispara o seguinte. Como classificá-los?',
    'O primeiro é síncrono; o segundo é assíncrono em cascata.',
    ['O primeiro é assíncrono; o segundo é síncrono.', 'Ambos são combinacionais e não possuem estado.', 'Ambos são necessariamente memórias ROM.', 'O compartilhamento de clock elimina qualquer atraso físico de propagação.'],
    ['Observe qual sinal chega à entrada de clock de cada flip-flop.', 'Clock comum caracteriza o contador síncrono.', 'Clock propagado entre estágios caracteriza a cascata assíncrona; isso não implica atrasos físicos nulos.'],
    'Síncrono significa referência comum de clock, não ausência de atraso físico.')
item('contadores', 'anel', 'Contador em anel', ['anel'],
    'Um indicador luminoso deve deslocar um único bit ativo por quatro posições e depois repetir a sequência. Que cuidado é necessário ao usar um contador em anel simples?',
    'Inicializar um único estágio com um e os demais com zero para circular o bit ativo.',
    ['Inicializar todos com zero e esperar que o deslocamento crie sozinho um bit um.', 'Eliminar os elementos de memória.', 'Trocar o clock por uma memória somente de leitura.', 'Manter todas as saídas permanentemente em um para representar uma única posição.'],
    ['Represente o estado inicial, por exemplo 0001.', 'Desloque com realimentação: 0010, 0100, 1000 e retorno.', 'Observe que 0000 apenas recircula zeros, por isso a inicialização faz parte do projeto.'],
    'A realimentação não cria espontaneamente o bit ativo numa cadeia inicializada só com zeros.')

item('logica_sequencial', 'd', 'Flip-flop D', ['flip', 'tipo d'],
    'Um registrador usa flip-flops D disparados na borda de subida, sem entradas assíncronas ativas. D muda entre duas bordas. Quando o novo valor passa a ser armazenado em Q?',
    'Na próxima borda de subida válida, respeitados os requisitos de temporização.',
    ['Imediatamente a cada alteração em D, independentemente do clock.', 'Somente quando D for igual a zero.', 'Apenas se o componente não tiver memória.', 'Q sempre armazena o complemento de D.'],
    ['Identifique a borda de disparo definida no enunciado.', 'Entre bordas, o flip-flop mantém o estado, nas condições indicadas.', 'Na borda válida, copia D para Q; não confunda esse comportamento com transparência de um latch.'],
    'Um flip-flop disparado por borda não acompanha continuamente D.')
item('logica_sequencial', 'jk', 'Flip-flop JK', ['jk'],
    'Um flip-flop JK ideal recebe J=K=1 na borda ativa, sem comandos assíncronos. Que comportamento é esperado?',
    'A saída alterna: o próximo estado é o complemento do estado atual.',
    ['A saída sempre permanece igual.', 'A saída sempre é forçada a zero.', 'A saída sempre é forçada a um.', 'O estado 11 é necessariamente proibido como no latch SR básico.'],
    ['Localize a linha J=1, K=1 na tabela característica.', 'Distinga os casos manter, setar, resetar e alternar.', 'Aplique a alternância: se Q era zero passa a um; se era um passa a zero.'],
    'A condição 11 do JK não deve ser confundida com a condição proibida do latch SR básico.')

item('maquinas_de_estados_finitos', 'moore', 'Máquina de Moore', ['moore'],
    'Em um semáforo modelado por máquina de estados, a cor exibida é determinada somente pelo estado atual. Qual modelo descreve essa saída?',
    'Moore: a saída é função do estado atual.',
    ['Mealy: a saída depende obrigatoriamente apenas da entrada.', 'Um circuito sem memória, pois há estados.', 'Uma máquina com infinitos estados por definição.', 'Uma porta NOT isolada, independentemente das transições.'],
    ['Identifique de quais variáveis a saída depende.', 'Separe saída das regras de transição: entradas ainda podem influenciar o próximo estado.', 'Como a saída foi associada apenas ao estado atual, classifique o modelo como Moore.'],
    'A dependência das transições em relação às entradas não transforma, sozinha, uma máquina de Moore em Mealy.')
item('maquinas_de_estados_finitos', 'mealy', 'Máquina de Mealy', ['mealy'],
    'Uma catraca emite um sinal de liberação em função do estado atual e da entrada que informa um pagamento válido. Qual modelo é compatível com essa regra de saída?',
    'Mealy: a saída pode depender do estado atual e da entrada.',
    ['Moore: a saída depende diretamente da entrada e nunca do estado.', 'Uma máquina sem estados, necessariamente.', 'Uma memória RAM que dispensa transições.', 'Um contador que obrigatoriamente só possui um estado.'],
    ['Separe a entrada pagamento do estado armazenado.', 'Observe que a regra de saída consulta os dois.', 'Reconheça Mealy; em Moore, a saída é associada somente ao estado.'],
    'Ter estados não basta para distinguir Mealy de Moore; examine a função de saída.')

item('memoria_rom', 'nao_volatil', 'Memória ROM e persistência', ['rom'],
    'Um equipamento precisa preservar instruções de inicialização mesmo quando a alimentação é desligada. Que característica torna uma memória ROM apropriada?',
    'A retenção não volátil das informações gravadas.',
    ['A perda obrigatória de todos os dados ao desligar.', 'A necessidade de reescrever cada bit a todo instante para preservar os dados sem energia.', 'A impossibilidade de armazenar instruções.', 'O fato de ser sempre mais rápida que qualquer outra memória em qualquer sistema.'],
    ['Identifique o requisito: conservar informação sem alimentação.', 'Diferencie volatilidade de velocidade e capacidade.', 'Selecione a característica não volátil da ROM, sem generalizar o desempenho de todas as tecnologias.'],
    'Persistência dos dados e velocidade de acesso são propriedades diferentes.')
item('memoria_rom', 'eeprom', 'ROM, PROM, EPROM e EEPROM', ['eeprom'],
    'Um projeto exige uma variante de ROM que permita apagar e reprogramar eletricamente seus dados. Qual opção corresponde ao requisito?',
    'EEPROM.', ['PROM de programação única.', 'EPROM apagada exclusivamente por luz ultravioleta.', 'ROM de máscara sem possibilidade de reprogramação.', 'Um registrador volátil sem armazenamento persistente.'],
    ['Separe programação única de memória reprogramável.', 'Distinga o método de apagamento: ultravioleta na EPROM e elétrico na EEPROM.', 'Escolha EEPROM porque o requisito especifica apagamento elétrico.'],
    'EPROM e EEPROM não são sinônimos; o método de apagamento é decisivo.')

item('memorias', 'fifo', 'Memória FIFO', ['fifo'],
    'Um dispositivo recebe os dados A, B e C nessa ordem e deve entregá-los na ordem de chegada. Que organização atende ao requisito?',
    'FIFO: A sai antes de B e C.',
    ['LIFO: C deve sair primeiro para manter a ordem de chegada.', 'FIFO: C sai antes de A.', 'Uma organização sem ordem definida atende necessariamente ao requisito.', 'Apenas inverter todos os bits de cada dado.'],
    ['Anote a ordem de entrada: A, B, C.', 'O primeiro elemento recebido deve ser o primeiro retirado.', 'Relacione essa regra a First In, First Out, isto é, FIFO.'],
    'LIFO retira primeiro o elemento mais recente e inverte a ordem de retirada.')
item('memorias', 'lifo', 'Memória LIFO', ['lifo'],
    'Uma pilha recebe A, depois B e depois C. Nenhum outro elemento é inserido. Qual é a ordem das três retiradas em uma organização LIFO?',
    'C, B, A.', ['A, B, C.', 'B, A, C.', 'A, C, B.', 'B, C, A.'],
    ['Localize o topo: C foi inserido por último.', 'Retire C; o novo topo passa a ser B.', 'Retire B e depois A, aplicando a regra Last In, First Out a cada etapa.'],
    'Não mantenha a ordem de chegada: isso descreveria FIFO, não LIFO.')

item('circuitos_logicos_sequenciais', 'memoria', 'Circuitos combinacionais e sequenciais', ['sequenciais', 'estado'],
    'Um portão deve abrir, parar ou fechar a cada novo toque no mesmo botão, dependendo da ação anterior. Por que o controle exige estado?',
    'A mesma entrada pode exigir ações diferentes conforme a situação armazenada.',
    ['A saída depende exclusivamente da entrada atual e nunca do passado.', 'O botão precisa gerar tensões contínuas com infinitos valores.', 'Qualquer porta AND isolada armazena toda a sequência.', 'Memória impede a construção de circuitos digitais.'],
    ['Compare dois toques iguais em momentos diferentes.', 'Perceba que o controlador precisa distinguir aberto, parado ou em movimento.', 'Conclua que a memória do estado diferencia o circuito sequencial de uma função apenas combinacional.'],
    'Entrada atual igual não garante saída igual quando o circuito possui estado.')
item('circuitos_logicos_sequenciais', 'blocos', 'Estado e lógica de próximo estado', ['estado'],
    'No modelo de um circuito sequencial, qual é a função dos elementos de memória em relação à lógica combinacional?',
    'Guardar o estado atual, utilizado pela lógica que calcula o próximo estado.',
    ['Substituir todos os sinais de entrada por valores aleatórios.', 'Eliminar a dependência temporal de qualquer circuito.', 'Armazenar obrigatoriamente um número infinito de estados.', 'Impedir que as saídas participem de qualquer realimentação.'],
    ['Identifique o que precisa ser conservado entre eventos.', 'Associe essa informação ao estado atual guardado na memória.', 'A lógica de próximo estado usa entradas e estado; a memória conserva o resultado conforme o funcionamento do circuito.'],
    'Lógica combinacional calcula; a memória conserva o estado entre eventos.')

item('introducao_a_eletronica_digital', 'representacao', 'Representação digital', ['digital', 'analógico'],
    'Uma equipe quer registrar digitalmente uma grandeza física contínua. Qual afirmação evita confundir o fenômeno físico com a forma de representá-lo?',
    'A grandeza pode continuar sendo contínua mesmo quando seus valores são representados digitalmente.',
    ['Representar digitalmente torna o fenômeno físico necessariamente binário.', 'A representação digital garante erro nulo em qualquer medição.', 'Grandezas contínuas não podem fornecer dados a sistemas digitais.', 'Digital e analógico se distinguem apenas pela quantidade de fios.'],
    ['Separe o fenômeno da informação usada para descrevê-lo.', 'Reconheça que um sistema digital manipula uma representação em estados discretos.', 'Conclua que a representação não muda a natureza contínua do fenômeno original.'],
    'A representação dos dados não transforma a natureza física da grandeza medida.')
item('introducao_a_eletronica_digital', 'projeto', 'Projeto de circuitos digitais', ['projeto'],
    'Antes de escolher componentes de um controlador digital, a equipe precisa definir seu comportamento. Qual ação oferece uma base adequada para o projeto?',
    'Especificar entradas, saídas e as relações de funcionamento exigidas.',
    ['Escolher componentes aleatórios e só depois decidir o objetivo.', 'Ignorar os valores lógicos das entradas.', 'Assumir que qualquer circuito atende a qualquer função.', 'Eliminar a necessidade de verificar o comportamento projetado.'],
    ['Descreva o problema e os sinais que representam as condições.', 'Defina como as saídas devem responder às entradas e, quando necessário, ao estado.', 'Use a especificação como referência para implementar e conferir o circuito.'],
    'Escolher componentes sem especificar o comportamento não permite verificar se o objetivo foi atendido.')

item('projetos_de_circuitos_sequenciais', 'diagrama', 'Diagrama de estados', ['diagrama', 'estados'],
    'Para projetar um portão automático, uma equipe desenha os estados fechado, abrindo, aberto e fechando. O que deve acompanhar as transições no diagrama?',
    'As condições ou eventos que levam de um estado ao próximo.',
    ['Apenas o nome comercial do fabricante.', 'Somente o tamanho físico do circuito.', 'Conexões aleatórias, pois as entradas não influenciam transições.', 'Uma regra que obriga todos os estados a terem saídas idênticas.'],
    ['Liste as situações que o sistema precisa distinguir.', 'Para cada evento, pergunte de qual estado ele parte e para qual deve ir.', 'Rotule as transições com as condições correspondentes para tornar o comportamento verificável.'],
    'Enumerar estados sem especificar transições deixa o projeto incompleto.')
item('projetos_de_circuitos_sequenciais', 'latch', 'Latch SR com portas NOR', ['latch', 'sr'],
    'Um latch SR básico com portas NOR e entradas ativas em nível alto recebe S=R=0, depois de ter sido colocado em um estado válido. O que acontece?',
    'Mantém o estado anteriormente armazenado.',
    ['Q é sempre forçado a um.', 'Q é sempre forçado a zero.', 'Q alterna automaticamente sem outro evento.', 'O caso 00 é a condição proibida desse latch NOR.'],
    ['Confira a implementação: NOR, entradas ativas em nível alto.', 'Com S=R=0 não há comando de set nem de reset.', 'A realimentação mantém o estado válido anterior; a condição problemática desse latch é S=R=1.'],
    'A tabela do latch NOR não deve ser trocada pela tabela de um latch NAND com entradas ativas em nível baixo.')

item('memoria_rom', 'prom', 'Memória PROM', ['prom'],
    'Um fabricante precisa gravar o conteúdo uma única vez após a fabricação do componente, sem prever apagamento para novas gravações. Qual variante de ROM corresponde a esse cenário?',
    'PROM de programação única.', ['EEPROM reprogramável eletricamente.', 'EPROM com apagamento ultravioleta.', 'RAM volátil.', 'Um flip-flop D sem armazenamento persistente.'],
    ['Verifique se a gravação ocorre na fabricação ou posteriormente.', 'O requisito exclui apagamento e reprogramação.', 'A PROM de programação única permite a programação posterior, mas não foi feita para ciclos de apagamento.'],
    'Não confunda programação única da PROM com reprogramação de EPROM e EEPROM.')
item('memoria_rom', 'eprom', 'Memória EPROM', ['eprom', 'ultravioleta'],
    'Um técnico identifica uma memória ROM reprogramável cujo apagamento utiliza luz ultravioleta. Qual é a tecnologia descrita?',
    'EPROM.', ['EEPROM, cujo apagamento exige obrigatoriamente luz ultravioleta.', 'PROM de programação única.', 'RAM volátil.', 'ROM de máscara sem possibilidade de apagar.'],
    ['Identifique que o componente pode ser apagado e reprogramado.', 'Use o método de apagamento como critério de distinção.', 'Luz ultravioleta caracteriza a EPROM; apagamento elétrico caracteriza a EEPROM.'],
    'A sigla EEPROM acrescenta a possibilidade de apagamento elétrico; não a troque por EPROM.')
item('memoria_rom', 'mascara', 'ROM de máscara', ['máscara'],
    'Um lote de equipamentos receberá um conteúdo fixado durante a fabricação da ROM, sem programação posterior pelo usuário. Qual tipo corresponde à descrição?',
    'ROM de máscara.', ['PROM que depende de programação posterior pelo usuário.', 'EEPROM para ciclos de reprogramação elétrica.', 'RAM que perde o conteúdo ao desligar.', 'Um contador binário crescente.'],
    ['Identifique o momento em que o conteúdo é definido: fabricação.', 'Diferencie essa definição da programação posterior de uma PROM.', 'Associe o conteúdo fixado pelo processo de fabricação à ROM de máscara.'],
    'A família ROM inclui tecnologias distintas; o momento e o método de programação importam.')

item('introducao_a_eletronica_digital', 'discretos', 'Níveis lógicos', ['níveis'],
    'Um sistema binário interpreta faixas de um sinal elétrico como zero ou um. O que representam esses dois valores no processamento digital?',
    'Dois estados lógicos usados para representar e manipular informação.',
    ['Todos os valores reais possíveis de uma grandeza contínua.', 'A garantia de que o circuito nunca sofre interferência.', 'Sempre exatamente zero volt e um volt em toda tecnologia.', 'A quantidade obrigatória de fios em qualquer equipamento.'],
    ['Distinga o valor lógico do valor exato da tensão.', 'Reconheça os dois estados aceitos pela representação binária.', 'Use zero e um como informação lógica, sem impor uma tensão universal.'],
    'Faixas de tensão dependem da implementação; zero e um representam estados lógicos.')
item('introducao_a_eletronica_digital', 'dados', 'Processamento de informação digital', ['dados'],
    'Um controlador recebe leituras, compara valores e decide uma ação. Na eletrônica digital, qual é o foco dessas operações?',
    'Representar e manipular dados para obter o comportamento desejado.',
    ['Eliminar a necessidade de componentes elétricos reais.', 'Garantir que toda grandeza física seja contínua no processamento.', 'Impedir que informações sejam armazenadas.', 'Usar apenas o formato externo do equipamento para decidir a saída.'],
    ['Identifique quais informações entram e qual decisão precisa sair.', 'Reconheça comparação e armazenamento como operações sobre dados.', 'Relacione essas operações à função do sistema digital no controlador.'],
    'O foco no processamento de dados não elimina a implementação elétrica do circuito.')
item('introducao_a_eletronica_digital', 'verificacao', 'Verificação de circuitos digitais', ['projeto'],
    'Depois de implementar um circuito, a equipe testa suas saídas para as situações previstas no projeto. Qual é o objetivo desse trabalho?',
    'Conferir se o comportamento implementado atende à especificação.',
    ['Modificar os requisitos silenciosamente para aceitar qualquer saída.', 'Concluir que uma única saída correta garante todas as demais.', 'Dispensar a análise das entradas.', 'Provar que não existe nenhum atraso físico possível.'],
    ['Retome a especificação de funcionamento.', 'Compare o resultado esperado com o obtido para cada situação testada.', 'Use divergências para revisar a implementação; um caso isolado não garante todos os outros.'],
    'Testar sem um resultado esperado definido não permite decidir se o comportamento está correto.')

item('algebra_booleana', 'mintermo', 'Mintermos', ['mintermo'],
    'Uma função de duas variáveis vale um apenas na linha A=1, B=0. Qual mintermo representa essa linha em uma soma de produtos?',
    'A AND (NOT B).', ['A AND B.', '(NOT A) AND B.', '(NOT A) AND (NOT B).', 'A OR B.'],
    ['Localize a linha em que a função deve valer um.', 'Em um mintermo, use cada variável sem negação quando ela vale um e negada quando vale zero.', 'Combine os literais com AND: A AND NOT B; o produto só vale um na linha indicada.'],
    'Não use OR entre os literais de um mintermo.')
item('algebra_booleana', 'maxtermo', 'Maxtermos', ['maxtermo'],
    'Em um produto de somas, deseja-se uma soma lógica que valha zero apenas na linha A=1, B=0. Qual maxtermo deve ser usado?',
    '(NOT A) OR B.', ['A OR B.', 'A OR (NOT B).', '(NOT A) OR (NOT B).', 'A AND (NOT B).'],
    ['Uma soma lógica vale zero quando todos os seus literais valem zero.', 'Para A=1 use NOT A; para B=0 use B.', 'Una os literais com OR: NOT A OR B; em qualquer outra linha pelo menos um literal vale um.'],
    'A regra de negação para formar o maxtermo não é a mesma usada para o mintermo da linha.')
