# Prática de Estrutura de Dados Avançada e Design

As disciplinas do terceiro período passam a oferecer prática autoral a partir das aulas, sem exigir uma prova do professor. A migration V12 habilita a funcionalidade; listas e provas continuam sujeitas às permissões próprias. Os slides precisam estar ativos e habilitados como fonte do Monitor Virtual.

## Estrutura de Dados Avançada

Em **Praticar**, selecionar **Estrutura de Dados Avançada**. Há conceitos, teste de mesa e seleção variada. A contextualização dos testes de mesa pode ser direta, cotidiana ou detalhada. O estado inicial, as regras e a convenção de altura são explícitos. A resolução contém tabela dos estados e explicação, exibidas após a resposta.

Cobertura: revisão de estruturas, conceitos de árvores, referências e nós em Python, aplicações de árvores, heap mínimo, ABB, árvores de decisão, trie, AVL, red-black, splay, ordenação e grafos. Apresentação e ementa não possuem exercícios. Os exercícios de rotações usam configurações pequenas e regras explícitas; não substituem a implementação completa das estruturas.

## Design de Artefatos Digitais

Banco inicial de **27 questões**, três por assunto, com situações-problema, cinco alternativas distintas e explicação da decisão. O formato é inspirado em questões contextualizadas do ENEM; não se trata de material oficial ou aproximação de uma prova do professor ainda não fornecida.

Os nove assuntos são introdução ao design, ferramentas visuais/identidade, público-alvo, comportamento do consumidor, interface, princípios de design, diagramação, Design Thinking e Matriz CSD. Cada questão exige uma fonte teórica do mesmo assunto, com referência de página; o texto do cenário é autoral.

Na atividade **Prova simulada por conteúdos**, selecionar um ou vários assuntos e entre 1, 3, 5 e 10 questões. A quantidade deve comportar pelo menos uma questão por assunto. A seleção própria do simulado prevalece sobre o assunto no cabeçalho. O servidor valida cada assunto e impede seleção de outra disciplina. A distribuição divide as questões entre os assuntos e redistribui cotas quando necessário, sem duplicar itens.

É possível alterar respostas antes da entrega. O envio para correção ocorre ao finalizar, e o resultado só aparece depois da correção de todas as questões. Falhas parciais mantêm as escolhas e permitem retomar as correções pendentes. A pontuação é a porcentagem de acertos, sem TRI. A tentativa usa a sessão de prática existente, com validade padrão de 60 minutos; não há histórico permanente de simulados nesta implementação. Recarregar a página perde as escolhas locais.

## Repetição e disponibilidade

Os fingerprints independem da ordem das alternativas e da contextualização. A prática evita questões recentes e permite revisar itens vistos quando não existem novos. Se um assunto escolhido para o simulado esgotou suas questões, não é montada uma prova que omita esse assunto. Seleções com menos questões disponíveis informam a quantidade efetiva. Um único assunto de Design tem até três itens distintos.

Não há chamadas ao provedor de texto para montar esses dois bancos. As respostas e os estados são derivados dos modelos locais conferidos. Gabarito e resolução ficam no serviço até a resposta, sem aparecer no payload inicial.

## Validação

`test_practice_avancada_design.py` confere os materiais reais, cobertura dos assuntos, três níveis de contextualização, resultados conhecidos, integridade das soluções, isolamento e seleção de conteúdos. `AvancadaDesignPraticaTests` verifica permissões e o contrato do servidor. `PraticaAvancadaDesign.test.jsx` cobre filtros, seleção múltipla, revisão de respostas, entrega e recuperação de falha parcial.
