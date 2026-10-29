# NEURON - Relatório geral para a equipe

**Referência: 28 de outubro de 2026 | Projeto Extensionista 2**

01 / VISÃO EXECUTIVA

## Relatório geral do projeto

NEURON | Projeto Extensionista 2

Situação atual, disciplinas cadastradas, funcionalidades, arquitetura, validações e preparação da apresentação. Data de referência: 28/10/2026.

### Decisão de escopo para a apresentação

A apresentação ficará limitada às cinco disciplinas já cadastradas. A inclusão de novas disciplinas fica adiada. O foco imediato é demonstrar o que já foi implementado, conferir o percurso de uso e alinhar a comunicação da equipe.

### O que é o NEURON

Plataforma web de apoio ao estudo que reúne materiais acadêmicos, um Monitor Virtual com inteligência artificial e prática com questões. O Monitor consulta os materiais da disciplina e do assunto selecionados, explica os conceitos e apresenta referências de arquivo e página.

| Disciplinas | Assuntos cadastrados | Materiais | Trechos registrados |
| --- | --- | --- | --- |
| 5 | 71 | 32 | 1.308 |

Totais consolidados das migrations V2 e V4-V7 e dos relatórios de integração. Os 1.308 registros incluem 15 origens de avaliações de Estatística; não são todos trechos teóricos usados pelo Monitor. Cadastro de assunto não equivale a cobertura integral da ementa.

### Situação da entrega

- Catálogo, biblioteca, Monitor Virtual, fontes e histórico integrados ao ambiente local nas cinco disciplinas.

- Prática disponível em Estatística e Sistemas Digitais, com regras e coberturas diferentes.

- Acesso local de visitante para explorar materiais e Monitor; conta de estudante necessária para demonstrar prática e avaliação.

- Publicação em produção, testes de carga e resultados de aprendizagem com alunos ainda não demonstrados nas evidências consultadas.

### Como ler este relatório

Esta emissão consolida código, documentação e resultados já existentes. Foram conferidos os cadastros e os XMLs disponíveis dos testes Java; não houve nova execução das suítes, chamada ao provedor de IA ou auditoria do banco em tempo real. Resultados históricos são identificados por etapa.

---

02 / ESCOPO CADASTRADO

## Disciplinas e materiais

As cinco disciplinas pertencem ao 3º período. O catálogo é carregado pela API; as migrations criam os registros e os scripts de integração vinculam os materiais ao índice de busca.

| Disciplina | Assuntos | Materiais | Trechos | Prática |
| --- | --- | --- | --- | --- |
| Estatística | 31 | 3 | 208 | Sim, cobertura limitada |
| Estrutura de Dados Avançada | 14 | 3 | 167 | Indisponível |
| Design de Artefatos Digitais | 9 | 9 | 363 | Indisponível |
| Projeto de Ideação de Software | 5 | 5 | 217 | Indisponível |
| Sistemas Digitais | 12 | 12 | 353 | Sim, questões autorais |
| Total | 71 | 32 | 1.308 | 2 disciplinas |

### Estatística

Um PDF teórico, uma lista em DOCX e uma prova anterior em PDF. São 193 trechos teóricos, seis registros da lista e nove da prova. A prática tem seis questões originais de múltipla escolha e geração de questões de IA limitada aos seis assuntos contemplados pelas avaliações autorizadas. A autoria oficial do gabarito da lista não está confirmada.

### Estrutura de Dados Avançada

Três PDFs: Aula_0, Aula_1 e Aula_2. Monitor e materiais organizados em 14 assuntos, com busca semântica e lexical. A prática permanece bloqueada até haver listas ou provas elegíveis e autorizadas.

### Design e Ideação

Design reúne oito aulas e um material complementar de Matriz CSD. Ideação reúne cinco aulas. Ambas têm biblioteca, Monitor com filtros, abertura das fontes e histórico. A ausência de avaliações autorizadas mantém a prática indisponível.

### Sistemas Digitais

Doze PDFs únicos, 189 páginas com texto e 353 trechos. Vinte páginas sem conteúdo útil foram excluídas da busca após conferência visual. Lista e prova não foram fornecidas. Há 32 questões conceituais autorais e sete famílias de exercícios lógicos e numéricos; a amostra validada contém 105 questões, não 105 questões fixas distintas.

Distribuição de arquivos: 31 PDFs e um DOCX. As contagens refletem o cadastro e os relatórios consultados, sem nova leitura do banco nesta emissão.

---

03 / O QUE A EQUIPE PODE DEMONSTRAR

## Funcionalidades e experiência

| Área | Comportamento implementado |
| --- | --- |
| Entrada e perfis | Login por sessão; perfis estudante, administrador e visitante. O visitante é habilitado para uso local pelo inicializador. |
| Disciplinas e biblioteca | Seleção de período, disciplina e assunto; materiais classificados; abertura dos arquivos e das páginas citadas quando disponíveis. |
| Monitor Virtual | Perguntas fundamentadas nos materiais; referências de arquivo/página; explicações, tabelas e esquemas textuais identificados como criação didática da IA. |
| Histórico | Conversas e fontes persistidas por conta, disciplina e assunto; reabertura após login. As oito mensagens recentes contextualizam continuações. |
| Prática | Seleção de assunto, origem, modo e quantidade; tentativa sem gabarito antecipado; correção com explicação e fontes. Estado vazio quando faltam questões. |
| Avaliação da plataforma | Envio voluntário por estudante: nota de 1 a 5 e comentário opcional de até 2.000 caracteres; possibilidade de atualizar a avaliação. |
| Administração de materiais | Controle de disponibilidade, uso no Monitor, prática e autorização; desativação e sincronização do índice. Administração completa do catálogo ainda fora do escopo. |

### Diferenças entre os acessos

- Estudante: consulta, Monitor, histórico da conta, prática nas disciplinas elegíveis e avaliação voluntária.

- Visitante: materiais e Monitor, com sessão isolada e histórico temporário; sem prática, avaliação ou administração. Dados removidos ao sair ou pela limpeza periódica após um dia.

- Administrador: permissões para controle dos materiais. A interface atual não representa um painel completo de gestão acadêmica.

### Interface e acessibilidade

Interface responsiva para computador, tablet e celular, com navegação adaptável, histórico móvel, foco visível, rótulos, atalho para pular ao conteúdo e respeito à preferência de movimento reduzido. As conferências documentadas abrangem larguras de 320, 768, 1024 e 1440 pixels; o fluxo real de Estatística também foi conferido em 390 × 844.

A prévia /qa/preview.html usa dados fictícios para conferir layout. A apresentação do funcionamento integrado deve usar a entrada real da aplicação.

---

04 / VISÃO TÉCNICA COMPARTILHADA

## Arquitetura e funcionamento

| Camada | Tecnologias e responsabilidade |
| --- | --- |
| Interface | React e Vite; seleção de contexto, biblioteca, chat, histórico, prática e avaliação. Acesso à API pública em /api. |
| API principal | Java com alvo 17, Spring Boot, Spring Security, JPA e Flyway; autenticação, permissões, catálogo, histórico e contratos públicos. |
| Serviço de IA | Python, FastAPI, LangChain, Sentence Transformers e cliente compatível com OpenAI para o OpenRouter; busca, geração e prática. |
| Dados | PostgreSQL para registros e conversas; pgvector para busca vetorial. Embeddings multilíngues locais de 384 dimensões. |

### Caminho de uma pergunta

1. O usuário escolhe disciplina e assunto e envia a pergunta. 2. O Spring verifica sessão, contexto e permissões. 3. O serviço de IA recebe a pergunta e o contexto recente. 4. O RAG recupera trechos permitidos, combinando recursos semânticos e lexicais conforme a disciplina. 5. O modelo gera a explicação. 6. A aplicação valida e apresenta as fontes e grava a troca no histórico.

O serviço interno usa /internal/v1 e token entre servidores. Chaves do provedor e credenciais do banco ficam no servidor. O SSE entrega eventos e fontes, mas o texto chega após a geração completa; ainda não há transmissão de cada token diretamente do provedor.

### Organização dos dados e materiais

Entidades centrais: usuário, período, disciplina, assunto, material, trechos de documento, conversa, mensagem e avaliação da plataforma. O catálogo relacional e o índice vetorial são separados: cadastrar uma disciplina não prepara automaticamente suas fontes. Os integradores conferem originais e metadados e associam trechos aos IDs dos materiais.

Migrations: V1 núcleo acadêmico; V2 Estatística; V3 histórico; V4 Estrutura de Dados; V5 Design; V6 Ideação; V7 Sistemas Digitais; V8 perfil visitante.

### Execução e manutenção local

São necessários PostgreSQL com pgvector, API Java, serviço de IA e interface. Endereços usuais: interface 127.0.0.1:5173, API 127.0.0.1:8080 e IA 127.0.0.1:8000. A porta da interface pode variar. O README contém preparação, comandos e solução dos problemas de inicialização.

A geração de respostas depende de internet, credencial e disponibilidade do OpenRouter. O modelo local de embeddings precisa estar em cache ou ser baixado previamente. O /health da IA confirma o serviço HTTP, sem garantir banco ou provedor disponíveis.

---

05 / RESULTADOS POR ETAPA

## Validações e evidências

Os resultados abaixo pertencem a execuções já registradas. Não devem ser somados como uma única suíte atual, porque várias etapas repetem os mesmos testes.

| Evidência | Resultado registrado e alcance |
| --- | --- |
| XMLs Java disponíveis | Conferência nesta emissão: 58 testes, 0 falhas, 0 erros e 0 ignorados. Incluem visitante e Sistemas Digitais. Não foram reexecutados. |
| Etapa de Ideação | 46 testes Java, 123 Python e 20 de interface aprovados na documentação; integração com cinco assuntos e cinco PDFs. |
| Etapa de Sistemas Digitais | 21 testes Python direcionados, 56 Java e 22 de interface registrados; build da interface concluído. Busca nos 12 assuntos e amostra de 105 questões geradas e corrigidas. |
| RAG conversacional | 16 cenários aprovados em quatro disciplinas: Estatística, Estrutura de Dados, Design e Ideação. Incluem continuação e pergunta sem cobertura nos materiais. |
| Estatística integrada | 31 assuntos conferidos na busca; 24 cenários HTTP na etapa de backend; nove cenários pela origem da interface na etapa posterior; cinco questões geradas conferidas independentemente. |
| Design e Ideação com provedor | Relatórios aprovados para pergunta real via API pública, resposta com fontes e reabertura pelo histórico. Contas temporárias removidas. |

### O que os testes demonstram

Há evidências de integração entre as camadas, recuperação de fontes, controle de acesso, preservação de materiais, isolamento do histórico e correção de amostras de prática. O relatório de Sistemas Digitais não incluiu nova geração de resposta do Monitor pelo provedor: nessa etapa foram verificadas busca, prática e testes existentes do Monitor.

### Limite da comprovação

Aprovação de cenários não garante correção acadêmica de todas as respostas futuras. Os registros não substituem ensaio no computador da apresentação, revisão docente, medição de aprendizagem ou avaliação de produção. O total antigo de 165 testes e 955 trechos pertence a uma etapa anterior e não representa o panorama consolidado atual.

---

06 / COMPROMISSOS DA ENTREGA

## Qualidade, limites e pendências

### Controles já implementados

- Sessões com cookies HttpOnly e proteção CSRF; operações administrativas restritas; token entre os serviços.

- Histórico acessível apenas ao dono e dentro do contexto da conversa; materiais indisponíveis ou revogados bloqueados na recuperação.

- Referências inexistentes são rejeitadas. Sem suporte suficiente, o Monitor deve declarar a limitação ou pedir esclarecimento.

- Na prática, gabarito e resolução permanecem no servidor até a tentativa; permissões são conferidas novamente na correção. Reenvio da mesma resposta preserva o resultado.

- Arquivos originais e páginas de origem preservados; exemplos e resoluções autorais de IA identificados separadamente do conteúdo acadêmico.

| Limite ou pendência | Impacto para a equipe |
| --- | --- |
| Cobertura das disciplinas | Prática de Estatística limitada aos assuntos elegíveis. Estrutura de Dados, Design e Ideação sem avaliações autorizadas para prática. |
| Sistemas Digitais | Lista e prova ausentes; faltam PDFs próprios de Sistema de numeração, Codificadores/decodificadores, Multiplexadores/demultiplexadores e RAM/cache. A extração textual não transcreve integralmente todos os circuitos e fórmulas gráficos. |
| Memória e prática | Contexto recente limitado a oito mensagens. Sessões de prática são temporárias, com expiração padrão de 60 minutos e estado em memória; manter um worker da IA. |
| Infraestrutura | Hospedagem pública, operação em escala, carga e configuração de produção pendentes. Configuração atual é local; acesso visitante não equivale a acesso público remoto. |
| Funcionalidades futuras | Monitoria humana, mensagens com monitores, agendamento, upload genérico, cadastro público e administração completa não estão implementados. |
| Preparação do ambiente | Dependências Python ainda não estão integralmente descritas no requirements inicial; seguir os complementos do README e ensaiar no ambiente preparado. |

Não há dados suficientes nos registros consultados para afirmar número de alunos atendidos, impacto educacional, custo mensal, prazo de publicação ou atribuir tarefas a integrantes específicos.

---

07 / APRESENTAÇÃO COM O ESCOPO ATUAL

## Roteiro e alinhamento da equipe

Roteiro sugerido de aproximadamente 10 a 12 minutos. As perguntas são exemplos para ensaio; novas respostas de IA dependem do ambiente e das fontes recuperadas.

| Tempo | O que mostrar |
| --- | --- |
| 1 min | Apresentar a proposta: organizar materiais, tirar dúvidas com referências e praticar com explicações. Informar o recorte das cinco disciplinas do 3º período. |
| 1 min | Abrir o catálogo real e a biblioteca. Mostrar que disciplina e assunto delimitam o conteúdo consultado. |
| 3 min | No Monitor, perguntar sobre pilhas em Estrutura de Dados; pedir outra explicação; abrir a fonte e reabrir o histórico. Mostrar brevemente Design Thinking e Lean Canvas nas disciplinas correspondentes. |
| 2 min | Entrar com conta de estudante preparada. Demonstrar questão de Estatística, tentativa, correção e fontes; explicar a diferença entre questão dos materiais e questão autoral de IA. |
| 2 min | Em Sistemas Digitais, selecionar uma questão de portas lógicas ou contadores, responder e mostrar os passos. Explicar que a fonte é teórica e que lista/prova ainda não foram fornecidas. |
| 1-2 min | Mostrar adaptação da interface e avaliação voluntária. Encerrar com arquitetura, evidências e limites atuais. |

### Conferência antes de apresentar

- Confirmar os cinco cadastros e a abertura dos materiais no ambiente real. Aguardar o carregamento completo da IA e conferir banco e provedor.

- Preparar uma conta de estudante para a prática; explorar sem conta serve à parte de materiais e Monitor. Evitar expor credenciais na projeção.

- Ensaiar as perguntas, conferir fontes e deixar a conversa demonstrativa disponível. Explicar eventual falta de cobertura em vez de prometer resposta para qualquer tema.

- Ter capturas ou gravação dos fluxos como apoio, identificadas como registro anterior caso a rede ou o provedor fiquem indisponíveis.

### Divisão sugerida e próximos passos

A equipe pode distribuir a fala entre proposta e interface, arquitetura e dados, Monitor e fontes, prática e validação. Os responsáveis nominais e tempos finais ficam para definição interna. Até a apresentação, priorizar ensaio, estabilidade local e revisão dos exemplos. Depois, avaliar com professores e alunos, completar materiais das disciplinas existentes e planejar publicação. Novas disciplinas ficam para uma etapa posterior.

---

08 / APÊNDICE A - CATÁLOGO

## Mapa de assuntos cadastrados

Listagem extraída das migrations do projeto. A quantidade de assuntos não indica que todos disponham de questões de prática.

### Estatística (31)

Fundamentos de probabilidade; Análise combinatória; Probabilidade condicional e independência; Introdução à Estatística e tipos de dados; Variáveis aleatórias e distribuições; Medidas de tendência central; Medidas de dispersão e posição; Valor esperado e momentos; Correlação e associação; Distribuições de frequência; Representações gráficas; Planejamento e amostragem; Reamostragem e bootstrap; Estimação e intervalos para a média; Distribuição t e intervalos para a média; Estimação e intervalos para proporções; Qui-quadrado e intervalos para variância; Distribuição binomial; Distribuição geométrica; Distribuição de Poisson; Distribuição F e ANOVA; Caudas longas e QQ-plot; Normal, TCL e aproximação binomial; Experimentos e testes de hipóteses; Testes Z e t; Teste qui-quadrado de independência; Permutação e Monte Carlo; Regressão linear simples e múltipla; Avaliação de regressão; Validação cruzada; Seleção de modelos e stepwise.

### Estrutura de Dados Avançada (14)

Apresentação e ementa; Revisão de estruturas em C; Conceitos de árvores; Árvores em Python; Aplicações de árvores; Filas de prioridade e heap; Árvores binárias de busca; Árvores de decisão; Árvore trie; Árvores balanceadas e AVL; Árvores red-black; Árvore splay; Algoritmos de ordenação; Grafos.

### Design de Artefatos Digitais (9)

Introdução ao Design; Ferramentas visuais; Público-alvo; Comportamento do consumidor; Design de interface; Princípios de Design; Design de interface: diagramação; Design Thinking; Matriz CSD.

### Projeto de Ideação de Software (5)

Introdução; Lean Canvas; Histórias de Usuário; Mapa de Navegação e Wireframe; Matriz CSD.

### Sistemas Digitais (12)

Sistemas analógicos e digitais; Portas lógicas e circuitos digitais; Álgebra booleana; Circuitos lógicos; Contadores; Lógica sequencial - Flip-flops e registradores; Máquinas de estados finitos; Memória ROM; Memórias - ROM, RAM, FIFO e LIFO; Circuitos lógicos sequenciais; Introdução à eletrônica digital; Projetos de circuitos sequenciais.

---

09 / APÊNDICE B - FONTES INTERNAS

## Documentação e rastreabilidade

Caminhos relativos à pasta NEURON. As fontes abaixo permitem à equipe localizar implementação, procedimentos e resultados citados. Os relatórios desta emissão não substituem esses registros técnicos.

| Referência | Onde conferir |
| --- | --- |
| Visão e execução | README.md: proposta, tecnologias, configuração local, acesso e limitações. |
| Catálogo e migrações | backend/demo/src/main/resources/db/migration/: V1 a V8. As migrations V2, V4, V5, V6 e V7 sustentam as contagens de assuntos e materiais. |
| Interface e histórico | docs/FRONTEND_E_HISTORICO.md e docs/CHAT_CONVERSACIONAL_RAG.md. |
| Estatística | docs/BACKEND_ESTATISTICA.md e docs/FRONTEND_ESTATISTICA.md; saidas_testes/estatistica_validacao_final.json, estatistica_validacao_frontend.json e estatistica_integracao_materiais.json. |
| Estrutura de Dados | docs/BACKEND_ED_AVANCADA.md; saidas_testes/ed_avancada_integracao_materiais.json e ed_avancada_validacao_backend.json. |
| Design | docs/BACKEND_DESIGN.md; saidas_testes/design_integracao_materiais.json e design_validacao_backend.json. |
| Ideação | docs/BACKEND_IDEACAO.md; saidas_testes/ideacao_integracao_materiais.json e ideacao_validacao_backend.json. |
| Sistemas Digitais | docs/SISTEMAS_DIGITAIS.md; saidas_testes/sistemas_digitais_integracao.json, sistemas_digitais_validacao.json e sistemas_digitais_amostra_resolvida.json. |
| Conversa e fontes | saidas_testes/validacao_conversa_rag.json e validacao_backend_contexto.json. |
| Testes Java | backend/demo/build/test-results/test/TEST-*.xml: 58 testes sem falhas, erros ou ignorados nos arquivos conferidos nesta emissão. |
| Acesso visitante | backend/demo/src/main/java/com/Neuron/demo/auth/AuthController.java; usuario/VisitanteCleanup.java; scripts/servicos_local.py. |

Nos caminhos abreviados acima, saidas_testes/ e scripts/ pertencem a neuron-ai/. Os nomes de documentos e relatórios foram preservados para busca nos arquivos do projeto.

### Registro desta emissão

Relatório preparado em 28/10/2026 para comunicação interna e apoio à apresentação. Escopo confirmado pelo usuário: manter apenas as disciplinas já cadastradas. Nenhuma nova disciplina, material ou funcionalidade foi adicionada para produzir este documento.
