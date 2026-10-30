# NEURON — Roteiro de apresentação sobre Scrum

Duração sugerida: 10 a 12 minutos.

## Equipe

- Ana Beatriz Costa: Product Owner.
- Lucas Almeida Santos: Scrum Master.
- Rafael Oliveira Lima: Developer.

## Slide 1 — NEURON

**Quem apresenta:** Equipe

Apresentação do trio: nosso produto é o NEURON, uma plataforma web do Projeto Extensionista 2. Vamos mostrar como organizamos uma Sprint para o fluxo do Monitor Virtual, passando pelo planejamento, acompanhamento, entrega e melhoria do trabalho.

## Slide 2 — O produto e a visão do PO

**Quem apresenta:** Ana · Product Owner

Nossa visão é facilitar o acesso ao conteúdo e apoiar a autonomia do estudante. O NEURON reúne materiais por disciplina e assunto, Monitor Virtual, histórico e prática nas disciplinas habilitadas. Nesta Sprint, priorizamos o percurso de tirar uma dúvida, consultar a fonte e retomar a conversa. A IA consulta os materiais selecionados e informa quando falta conteúdo suficiente. Isso não substitui a orientação do professor.

## Slide 3 — Responsabilidades do trio

**Quem apresenta:** Lucas · Scrum Master

Ana representa as necessidades dos usuários e decide a ordem do backlog. Lucas ajuda o time a usar o Scrum e a resolver impedimentos. Rafael responde pelo plano de execução e pela qualidade do incremento. As decisões de planejamento envolvem o time. O Scrum Master não distribui tarefas como um chefe. O Developer adapta o plano de trabalho durante a Sprint.

| Integrante | Papel | Responsabilidade |
| --- | --- | --- |
| Ana Beatriz Costa | Product Owner | Define o objetivo do produto e ordena o backlog pelo valor ao estudante. |
| Lucas Almeida Santos | Scrum Master | Apoia o uso do Scrum e ajuda a remover impedimentos. |
| Rafael Oliveira Lima | Developer | Planeja a execução, integra as funcionalidades e verifica a qualidade. |

## Slide 4 — Product Backlog priorizado

**Quem apresenta:** Ana · Product Owner

Priorizamos o fluxo central de estudo. Primeiro, o aluno precisa conseguir perguntar. Depois, conferir a origem da explicação e voltar à conversa. A adaptação ao celular faz parte desse percurso. A prática e a avaliação ficam para a etapa seguinte deste planejamento. O projeto já tem essas funcionalidades, com prática restrita às disciplinas e aos materiais habilitados. A tabela organiza o recorte do desenvolvimento apresentado, e não pretende listar tudo que existe hoje no NEURON.

| Ordem | Item e valor para o estudante | Destino |
| --- | --- | --- |
| 01 | US01 · Perguntar ao Monitor com o contexto da disciplina | Sprint 1 |
| 02 | US02 · Abrir o arquivo e a página usados na resposta | Sprint 1 |
| 03 | US03 · Reabrir a conversa com mensagens e fontes | Sprint 1 |
| 04 | US04 · Usar o fluxo no computador e no celular | Sprint 1 |
| 05 | US05 · Praticar questões com correção explicada | Etapa seguinte |
| 06 | US06 · Avaliar a plataforma com nota e comentário | Etapa seguinte |

## Slide 5 — Sprint Planning

**Quem apresenta:** Rafael · Developer

Antes desta Sprint, consideramos disponíveis o acesso por conta e o catálogo de disciplinas. O PO explicou a prioridade e os critérios de aceitação. Como Developer, estimei esforço e dependências e selecionei os quatro itens com o time. Os pontos são estimativas relativas de complexidade, não horas. As tarefas incluem integrar a interface à API, recuperar trechos dos materiais, vincular referências, salvar a conversa e conferir o fluxo em telas diferentes. O plano pode mudar durante a Sprint para preservar o objetivo.

## Slide 6 — Critérios para concluir a entrega

**Quem apresenta:** Rafael · Developer

Os critérios de aceitação descrevem o comportamento esperado de cada história. A Definition of Done estabelece a qualidade exigida para que um item componha o incremento. Para US01, a pergunta precisa respeitar o contexto selecionado. Para US02, o link deve abrir o material correspondente. Para US03, a conversa deve preservar mensagens e fontes sem expor dados de outra conta. Para US04, o fluxo precisa permanecer utilizável em computador e celular. O PO inspeciona o resultado na Review, e a qualidade é uma responsabilidade contínua do time.

## Slide 7 — Daily Scrum: ajuste do plano

**Quem apresenta:** Lucas e Rafael

Lucas: a Daily foi um encontro curto para inspecionar o avanço em direção ao objetivo e adaptar o trabalho. Rafael: identifiquei que mostrar o histórico na tela não bastava. A API também precisava enviar mensagens recentes à IA. Passei a priorizar esse ajuste antes de concluir o fluxo. Lucas: a investigação detalhada ocorreu depois da Daily, evitando alongar o encontro. A Daily é voltada aos Developers. PO e Scrum Master participam quando contribuem nesse papel, e o apoio à remoção de impedimentos pode ocorrer depois da reunião.

## Slide 8 — Incremento: Monitor com fontes e histórico

**Quem apresenta:** Rafael · Developer

Demonstrar o percurso: entrar com uma conta preparada, selecionar Estrutura de Dados Avançada e perguntar ‘O que são pilhas?’. Em seguida, pedir outra explicação, conferir a referência à Aula 0, página 14, e reabrir a conversa no histórico. A captura registra a interface do projeto em 28/10/2026. O Monitor usa busca nos materiais e contexto recente. As mensagens de uma conta não ficam disponíveis para outra. A entrega opera em ambiente local, com dependência do banco, dos materiais preparados e do provedor de IA.

## Slide 9 — Sprint Review: feedback do produto

**Quem apresenta:** Ana · Product Owner

Na Review, apresentamos o incremento e discutimos seu uso com os participantes convidados. Mariana valorizou o acesso à fonte. O professor André chamou atenção para a diferença entre um exemplo novo da IA e o texto do material. Essa identificação já aparece no projeto e merece ser preservada nas próximas melhorias. Como PO, uso o feedback para ajustar a ordem do backlog. A Review serve para inspecionar o produto e discutir os próximos passos. A disponibilização pública continua como uma decisão posterior, pois a entrega atual é local.

## Slide 10 — Retrospectiva: melhorias no trabalho

**Quem apresenta:** Lucas · Scrum Master

A Retrospectiva se concentra em como trabalhamos. O grupo percebeu que deixar a integração para o fim aumentava o retrabalho. Rafael ficará responsável por conferir um percurso completo desde o primeiro dia. Ana revisará os critérios de aceitação antes do início de cada item. Lucas acompanhará os impedimentos e organizará o ensaio antes da Review. Na próxima Retrospectiva, o time verificará se essas ações reduziram problemas de integração e dúvidas sobre o resultado esperado.

## Slide 11 — Dificuldades e aprendizados por papel

**Quem apresenta:** Trio

Ana: meu principal aprendizado foi que priorizar exige escolher o que pode esperar. Lucas: aprendi que facilitar o Scrum exige acompanhar problemas concretos, além de organizar encontros. Rafael: aprendi que uma tela pronta não significa que o fluxo completo está integrado. A passagem do histórico para a IA mostrou a importância de verificar o comportamento de ponta a ponta.

| Papel | Dificuldade | Aprendizado |
| --- | --- | --- |
| Product Owner | Escolher entre muitas funcionalidades úteis. | Ordenar pelo valor do fluxo central e manter o foco da Sprint. |
| Scrum Master | Evitar reuniões longas e impedimentos parados. | Separar alinhamento de investigação e acompanhar a resolução. |
| Developer | Integrar interface, histórico e recuperação de fontes. | Testar o percurso completo e conferir as referências desde cedo. |

## Slide 12 — Entrega e próximos passos

**Quem apresenta:** Ana · Product Owner

Encerramos com um incremento utilizável para o objetivo definido. O NEURON também possui recursos de prática e avaliação que entram na continuidade deste planejamento. Não afirmamos melhoria medida no desempenho dos alunos, porque isso exige avaliação com usuários. A publicação e a operação em escala precisam de preparação própria. Nossa conclusão é que o Scrum ajudou a organizar o recorte de trabalho, tornar os impedimentos visíveis e orientar os próximos passos a partir da inspeção da entrega.

## Histórias e critérios de aceitação

### US01 — Perguntar ao Monitor
Como estudante, quero perguntar sobre o conteúdo da disciplina para compreender o assunto estudado.

Aceitação: usar disciplina e assunto selecionados na recuperação de materiais; apresentar resposta apoiada em fontes; informar quando não houver suporte suficiente.

### US02 — Conferir a fonte
Como estudante, quero abrir o arquivo e a página citados para conferir a explicação.

Aceitação: exibir arquivo e página na referência; abrir a fonte disponível; bloquear acesso a materiais indisponíveis.

### US03 — Retomar a conversa
Como estudante, quero reabrir minhas conversas para continuar o estudo.

Aceitação: persistir mensagens e fontes por usuário; recuperar a conversa no contexto correto; usar as mensagens recentes para compreender continuações; impedir acesso ao histórico de outra conta.

### US04 — Estudar em telas diferentes
Como estudante, quero usar o Monitor no celular e no computador para estudar nos dispositivos que tenho disponíveis.

Aceitação: manter seleção de contexto, envio de perguntas e acesso às referências utilizáveis nas duas telas.

## Sequência da demonstração

1. Entrar com uma conta preparada e abrir o Monitor Virtual.
2. Selecionar Estrutura de Dados Avançada.
3. Perguntar: “O que são pilhas?”.
4. Pedir: “Explique melhor e mostre um exemplo”.
5. Abrir uma fonte apresentada na resposta.
6. Reabrir a conversa no histórico.
7. Mostrar o mesmo fluxo na tela de celular ou a captura correspondente.

## Distribuição de tempo

| Parte | Tempo sugerido |
| --- | --- |
| Abertura, produto e papéis | 2 minutos |
| Backlog e Planning | 2 minutos |
| Qualidade e Daily | 2 minutos |
| Incremento e demonstração | 2 minutos |
| Review e Retrospectiva | 2 minutos |
| Aprendizados e fechamento | 1 minuto |

## Perguntas para o ensaio

**Por que a Daily?** Para o Developer inspecionar o avanço em direção ao objetivo da Sprint e adaptar o plano de trabalho. O encontro tem limite de 15 minutos.

**Qual a diferença entre Review e Retrospectiva?** Na Review, o time e os participantes inspecionam o produto e discutem o backlog. Na Retrospectiva, o time inspeciona sua forma de trabalhar e escolhe melhorias.

**O que os pontos medem?** Uma estimativa relativa de esforço e complexidade, incluindo incerteza. Treze pontos não significam treze horas nem uma velocidade já comprovada.

**O que é o incremento?** O resultado integrado e utilizável que atende à Definition of Done. Nesta Sprint, é o fluxo do Monitor com referências, histórico e adaptação às telas.

**A IA responde a qualquer pergunta?** A cobertura depende dos materiais disponíveis. Quando falta suporte, o Monitor deve informar a limitação.

**A prática está disponível em todas as disciplinas?** Não. Depende da disciplina, dos materiais habilitados e das regras de prática implementadas.
