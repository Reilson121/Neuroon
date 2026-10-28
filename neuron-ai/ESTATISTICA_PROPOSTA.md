# Estatística no NEURON — inventário e proposta para validação

Registro da proposta inicial de 27/10/2026. O usuário aprovou posteriormente o mapa. O estado atual da implementação, as decisões confirmadas e as pendências de processamento estão em `MONITOR_ESTATISTICA.md`. As seções abaixo preservam o inventário e a proposta apresentados para essa aprovação.

## Materiais e preservação

Período 03, confirmado pelo usuário. Origem: `C:\Users\Pichau\Downloads\Estatística-20261027T153405Z-1-001\Estatística`.

Cópias em `materiais_academicos/periodo_03/estatistica/`. Os quatro arquivos mantêm seus nomes, bytes, datas de criação e de modificação. Os hashes SHA-256 das cópias conferem com os originais. O inventário detalhado, incluindo caminhos, hashes e metadados PDF, está em `propostas/estatistica/inventario.json`.

| Arquivo original | Tipo proposto | Conteúdo e situação |
| --- | --- | --- |
| `estatistica_novo.pdf` | `SLIDE_AULA` | 176 páginas, um slide por página. Fonte teórica principal. Autor nos metadados: Jonatas Junior. PDF produzido pelo PowerPoint; não foi fornecido o PPTX. |
| `Exercissios 1 Unidade.docx` | `LISTA_EXERCICIOS` | Seis questões, numeradas 1, 2, 5, 6, 7 e 9. Contém gabarito das quatro questões de múltipla escolha e resoluções das duas questões de cálculo. A autoria e o caráter oficial dessas notas não estão confirmados. |
| `prova anterior de estátisitica.pdf` | `PROVA_ANTIGA` | Duas páginas digitalizadas; nove questões, seis de múltipla escolha e três de cálculo. Cabeçalho: Estatística Computacional, professor Jonatas da Silva Junior, data preenchida como 01/10/2024. Contém marcações e cálculos manuscritos; não há um gabarito oficial completo identificado. |
| `rotacoes.py` | Fora da disciplina; sem tipo acadêmico atribuído | Implementação de rotações e inserção em árvores AVL. Copiado para preservar o conjunto recebido, sem execução e fora do mapa e da prática de Estatística. |

Não foram encontradas outras listas, outras provas ou arquivos separados de gabarito no diretório indicado nem no conjunto acadêmico do projeto. O DOCX não contém `docProps/core.xml`, `docProps/app.xml` ou paginação renderizada salva; não é possível atribuir uma página estável com base no pacote recebido. Suas referências devem usar o título e o número original da questão até existir uma paginação conferida.

O nome acadêmico da prova é **Estatística Computacional**. Propõe-se manter `estatistica` como identificador interno, conforme o nome solicitado, preservando o nome original do material nos metadados. Não se deve inferir número de aula para o PDF consolidado: o campo `aula` proposto é `null`.

## Ordem de navegação e mapa por assunto

As páginas abaixo são as posições físicas do PDF `estatistica_novo.pdf`, começando em 1. Os intervalos incluem os dois extremos. Esta tabela também define a ordem proposta de navegação. A sequência acompanha o material, agrupando as retomadas de um mesmo tema. Não há uma divisão por unidades explícita no PDF que justifique atribuir artificialmente os tópicos a unidades.

| Ordem | Assunto e identificador | Subassuntos identificados e páginas |
| --- | --- | --- |
| 1 | Fundamentos de probabilidade — `fundamentos_de_probabilidade` | Motivação e incerteza (2–3); experimento, resultado, espaço amostral e eventos (4); probabilidade clássica e empírica (6); lei dos grandes números, limites e complemento (7); união, interseção e eventos disjuntos (8–9); probabilidades e chances em nova exposição (43). |
| 2 | Análise combinatória — `analise_combinatoria` | Princípio fundamental da contagem e árvore de possibilidades (5); escolha e ordenação (13); arranjos (14); permutação simples (15), com repetição (16), circular (17) e de colares (18); combinações (19). |
| 3 | Probabilidade condicional e independência — `probabilidade_condicional_e_independencia` | Probabilidade condicional (10); regra do produto (11); independência e fórmulas equivalentes (12). |
| 4 | Introdução à Estatística e tipos de dados — `introducao_estatistica_e_tipos_de_dados` | Estatística descritiva e inferencial (21); dados estruturados e não estruturados (22); quantitativos e qualitativos, discretos e contínuos, nominais, ordinais e binários (23–24). |
| 5 | Variáveis aleatórias e distribuições — `variaveis_aleatorias_e_distribuicoes` | Variáveis discretas e contínuas, massa e densidade, probabilidade de ponto e de intervalo (25–28); finalidade de distribuições (78); condições de validade e construção de uma distribuição discreta a partir de frequências (107–108). |
| 6 | Medidas de tendência central — `medidas_de_tendencia_central` | Apresentação das medidas (30); média e mediana, sensibilidade a extremos (31); média ponderada e aparada (32); média geométrica e moda (33); relação entre média, mediana e assimetria (35). |
| 7 | Medidas de dispersão e posição — `medidas_de_dispersao_e_posicao` | Escore Z como posição relativa (34); apresentação das medidas (37); variância e desvio-padrão (38); desvio absoluto médio e amplitude (39); fractis, quartis, percentis, IQR e robustez (40); sumário de cinco números e boxplot (63). |
| 8 | Valor esperado e momentos — `valor_esperado_e_momentos` | Valor esperado e interpretação (42); média, variância, desvio-padrão e esperança de uma variável aleatória discreta (109). |
| 9 | Correlação e associação — `correlacao_e_associacao` | Coeficiente de correlação, direção e intensidade da associação linear (44); matriz de correlação e multicolinearidade (45); diagrama de dispersão e padrões de associação (61). Covariância aparece nas avaliações, mas não tem uma exposição própria nos slides. |
| 10 | Distribuições de frequência — `distribuicoes_de_frequencia` | Classes, limites e tamanho de classe (47); construção da tabela (48); dados do exemplo (49); ordenação e frequências absolutas (50); fronteiras, pontos médios, frequências relativas e acumuladas (51). |
| 11 | Representações gráficas — `representacoes_graficas` | Histograma (52–53), polígono de frequência (54), histograma relativo (55), ogiva (56), ramos e folhas (57), pontos (58), setores (59), Pareto (60) e série temporal (62). Dispersão e boxplot pertencem aos assuntos 9 e 7, respectivamente. |
| 12 | Planejamento e amostragem — `planejamento_e_amostragem` | Etapas de um estudo e objetivos (65–66); controle, aleatorização e replicação (67); população, amostra, parâmetro e estatística (68); formas de coleta e amostragem simples, estratificada, por agrupamento e sistemática (69); vieses de seleção, conveniência, cobertura, não resposta, autoseleção e erros humanos (70–72); prevenção (73). |
| 13 | Reamostragem e bootstrap — `reamostragem_e_bootstrap` | Reamostragem com reposição e estimação computacional da variabilidade (74). |
| 14 | Estimação e intervalos para a média — `estimacao_e_intervalos_para_media` | Estimativa pontual (75), intervalar (76), erro-padrão (77); nível de confiança e curva normal (79–80); erro amostral (81); margem de erro (82); intervalo e construção (83–84); tabela normal padrão de 0 a Z (85); interpretação frequentista (86); tamanho da amostra (87). |
| 15 | Distribuição t e intervalos para a média — `distribuicao_t_e_intervalos_para_media` | Estatística t e uso do desvio amostral (88); graus de liberdade (89); propriedades e comparação com normal (90); margem e intervalo (91–92); tabela t (93); escolha entre normal e t (94). |
| 16 | Estimação e intervalos para proporções — `estimacao_e_intervalos_para_proporcoes` | Proporção populacional e estimativa amostral (95–96); margem e intervalo (97); condições da aproximação e construção (98); tamanho de amostra com ou sem estimativa preliminar (99). |
| 17 | Qui-quadrado e intervalos para variância — `qui_quadrado_e_intervalos_para_variancia` | Estimação de variância e desvio (100); estatística qui-quadrado (101); propriedades e graus de liberdade (102); valores críticos esquerdo e direito (103); intervalos para variância e desvio (104–105); tabela (106). |
| 18 | Distribuição binomial — `distribuicao_binomial` | Condições do experimento (110); notação, sucesso e falha (111); fórmula da probabilidade (112); média, variância e desvio (113). |
| 19 | Distribuição geométrica — `distribuicao_geometrica` | Tentativas até o primeiro sucesso, independência, probabilidade constante e fórmula (114). |
| 20 | Distribuição de Poisson — `distribuicao_de_poisson` | Contagens em intervalos, condições e independência (115); fórmula e parâmetro médio (116). |
| 21 | Distribuição F e ANOVA — `distribuicao_f_e_anova` | Razão de variâncias, graus de liberdade e usos (117); variação entre e dentro dos grupos (118); tabela F (119); exemplo com médias, somas de quadrados, graus de liberdade e F (120–124); segunda aplicação com teste e conclusão (148–150). |
| 22 | Caudas longas e QQ-plot — `caudas_longas_e_qq_plot` | Valores extremos, caudas e assimetria (125); exemplos em dados reais (126); diagnóstico com QQ-plot (127); modelos citados: log-normal, Pareto, exponencial, Poisson e potência (128). Estes últimos são menções introdutórias, não capítulos completos nem uma classificação matemática validada de caudas. |
| 23 | Normal, TCL e aproximação binomial — `distribuicao_normal_tcl_e_aproximacao_binomial` | Teorema Central do Limite e curva normal (129); condições de aproximação da binomial (130); relação entre discreto e contínuo (131); correção de continuidade (132); procedimento, escore Z e tabela (133). A tabela normal também permanece referenciada no assunto 14, página 85, sem duplicar a página no mapa. |
| 24 | Experimentos e testes de hipóteses — `experimentos_e_testes_de_hipoteses` | Experimento controlado (135); hipóteses nula e alternativa e testes unilaterais e bilaterais (136); erros I e II e poder (137); p-valor e significância (138); etapas de teste e relato (139); A/B e A/B/C (140); visão dos testes t, qui-quadrado, ANOVA e permutação (141). |
| 25 | Testes Z e t — `testes_z_e_t` | Exemplo de teste de uma média denominado Z nos slides (143); comparação de duas médias, erro-padrão, estatística t, graus de liberdade e decisão (144–145). Os pressupostos exigem revisão antes de gerar questões. |
| 26 | Teste qui-quadrado de independência — `teste_qui_quadrado_de_independencia` | Tabela de contingência, frequências observadas e esperadas (146); estatística, graus de liberdade, valor crítico e associação (147). |
| 27 | Permutação e Monte Carlo — `testes_de_permutacao_e_monte_carlo` | Experimento com plantas e hipóteses (151–152); diferença de médias e combinações possíveis (153); permutações (154); p-valor exato e interpretação (155–156); motivação computacional (157); simulação de Monte Carlo e etapas em Python (158–159). |
| 28 | Regressão linear simples e múltipla — `regressao_linear_simples_e_multipla` | Previsão e relação com correlação (160); resposta, preditores, observações, inclinação, intercepto, ajuste e resíduo (161); mínimos quadrados e equações (162); coeficientes (163); múltiplos preditores e controle de variáveis (164). |
| 29 | Avaliação de regressão — `avaliacao_de_regressao` | RMSE (165), erro-padrão residual e graus de liberdade (166), RSS, TSS e R² (167), interpretação do R² por área nos slides (168), R² ajustado (169). Os limites apresentados por área não devem virar regras universais nas questões. |
| 30 | Validação cruzada — `validacao_cruzada` | Generalização e overfitting (171); procedimento K-fold (172); estratificação por classe (173); procedimento estratificado (174). |
| 31 | Seleção de modelos e stepwise — `selecao_de_modelos_e_stepwise` | Seleção de preditores, precisão e simplicidade, regressão passo a passo, critérios como R² ajustado e AIC (175); ruído, complexidade e overfitting (176). |

Páginas excluídas por serem capas ou separadores sem desenvolvimento: **1, 20, 29, 36, 41, 46, 64, 134, 142 e 170**. A chamada “Ver código” da página 20 não fornece um arquivo de Estatística no conjunto recebido; `rotacoes.py` não corresponde a essa chamada.

O mapa técnico proposto está em `propostas/estatistica/mapa_proposto.json`. Mantém a estrutura do mapa de Estrutura de Dados Avançada: `periodo`, `disciplina`, `arquivos`, `aula`, `assuntos`, `paginas_textuais` e `paginas_multimodais`. A proposta ainda **não** foi instalada em `app/rag/mapas/estatistica.py`; esse passo depende da validação solicitada pelo usuário.

Cada página tem exatamente um assunto principal, pois o processador existente rejeita sobreposições. Retomadas usam intervalos descontínuos no mesmo assunto. A distinção entre as distribuições t/qui-quadrado para estimação e os testes correspondentes evita misturar finalidades. A navegação pode remeter a pré-requisitos sem duplicar o conteúdo nem atribuir a mesma página a vários assuntos.

Propõem-se 63 páginas textuais e 103 multimodais. O uso visual contempla fórmulas com radicais ou frações, tabelas, gráficos e fluxogramas cujo conteúdo ou ordem não é preservado integralmente pela extração textual. A seleção é uma proposta de processamento, sem chamadas a serviços externos nesta etapa.

## Listas, prova e padrão de cobrança

| Questão original | Conceito e habilidade | Lista | Prova | Resposta ou resolução disponível |
| --- | --- | --- | --- | --- |
| 1 | Significado de mediana | Presente; múltipla escolha | Página 1; múltipla escolha | Lista: alternativa b. Há marcações na prova; não constituem um gabarito oficial completo. |
| 2 | Definição de amplitude | Presente; múltipla escolha | Página 1; múltipla escolha | Lista: alternativa b. |
| 3 | Interpretação de probabilidade condicional | Ausente | Página 1; múltipla escolha | Sem gabarito oficial separado. |
| 4 | Espaço amostral de duas moedas | Ausente | Página 1; múltipla escolha | Sem gabarito oficial separado. |
| 5 | Interpretação do desvio-padrão | Presente; múltipla escolha | Página 1; múltipla escolha | Lista: alternativa b. |
| 6 | Interpretação de covariância próxima de zero | Presente; múltipla escolha | Página 1; múltipla escolha | Lista: alternativa c. |
| 7 | Média, mediana, variância populacional e desvio-padrão de [2, 4, 6, 8, 10] | Presente; dois itens de cálculo | Página 2; dois itens de cálculo | Lista contém resolução: 6; 6; 8; √8 ≈ 2,83. Os valores conferem matematicamente. |
| 8 | Arranjos simples de três elementos entre 15 | Ausente | Página 2; cálculo | Sem gabarito oficial. O cálculo independente dá 15×14×13 = 2730; o manuscrito não deve ser convertido em resposta oficial. |
| 9 | Quartis e IQR, com contexto de tempos de login | Presente; dois itens de cálculo | Página 2; dois itens de cálculo | Lista contém resolução com interpolação pelas posições (n+1)q: Q1=3,5; Q2=8; Q3=12,5; IQR=9. Diverge do método dos slides. |

As seis questões da lista também aparecem na prova. São **nove enunciados distintos identificados**, não quinze questões independentes. A numeração original deve permanecer intacta e as origens devem ser associadas à mesma questão quando a equivalência for confirmada no cadastro. Subitens não devem perder seu vínculo com o enunciado principal.

O padrão observado combina definições e interpretação com alternativas a–e, cálculos curtos sobre pequenos conjuntos de dados e um contexto de desempenho computacional. As questões de cálculo da prova são abertas; convertê-las em múltipla escolha cria uma adaptação ou uma questão nova, que não deve ser exibida como o formato oficial da prova.

Há avaliação explícita de probabilidade básica e condicional, combinatória, tendência central, dispersão, quartis e associação. Não há lista ou prova disponível que permita afirmar o nível ou o estilo de cobrança de intervalos, demais distribuições, ANOVA, testes avançados, regressão e validação cruzada. Esses assuntos estão confirmados na teoria; sua prática baseada estritamente em questões cadastradas deve permanecer vazia enquanto não houver material elegível. Uma futura geração baseada em teoria exigirá uma política explícita e identificação como conteúdo de IA.

## Divergências e decisões pendentes

1. **Aprovação do mapa e da ordem.** Validar os 31 assuntos, suas faixas e a exclusão dos dez separadores. A aprovação do mapa não concede autorização de prática para listas ou provas.
2. **Convenção de quartis.** Na página 40 dos slides, o índice é `(n−1)q`, iniciando em zero. Para os dados da questão 9, resulta em Q1=4,5, Q2=8, Q3=11,5 e IQR=7. A lista usa `(n+1)q` em posições iniciadas em 1, obtendo Q1=3,5, Q2=8, Q3=12,5 e IQR=9. Ambos os cálculos foram conferidos. A futura questão deve declarar a convenção; é necessário confirmar qual adotar como padrão do curso.
3. **Origem do gabarito da lista.** O documento tem uma seção de notas com respostas, mas não identifica o autor ou o professor. Preservar como “gabarito contido no material, autoria não confirmada” até validação. Não anunciar como gabarito oficial do professor.
4. **Permissões de listas e provas.** Não há comprovação de autorização para prática no conjunto recebido. Confirmar separadamente o uso de questões originais, a consulta como referência para geração de questões inéditas e a disponibilidade aos alunos. A simples presença do arquivo e a aprovação do mapa não atendem esses requisitos.
5. **Correções dos slides.** Preservar o original e manter observações de revisão separadas. Antes de usar os trechos problemáticos para corrigir ou gerar questões, confirmar a política de revisão didática. Foram identificados os pontos abaixo; a inspeção desta etapa não é uma auditoria matemática completa de toda a apresentação.

| Página | Observação de revisão |
| --- | --- |
| 24 | “Número de campeonatos” aparece como exemplo de variável contínua, embora seja uma contagem. |
| 79–80 e 86 | As primeiras páginas usam linguagem de probabilidade/certeza sobre um intervalo já calculado; a página 86 faz a ressalva frequentista. Recuperar a ressalva junto da explicação para evitar respostas contraditórias. |
| 113 | A média e a variância binomiais estão escritas com `P(x)` em lugar do parâmetro de sucesso `p`; não transformar a notação equivocada em regra de correção. |
| 120–124 | Recalculando os dados originais: SQE=218/9, SQD=26/3 e F=109/13≈8,384615. Os slides usam valores intermediários arredondados, chegando a aproximadamente 8,41. |
| 128 | Os modelos citados não devem ser tratados indiscriminadamente como distribuições de cauda pesada. O material apenas os menciona no contexto de modelagem. |
| 143–145 | A página 143 denomina o procedimento “teste Z” usando desvio amostral e n=25. O exemplo de duas amostras usa gl=8, que requer a hipótese adequada para o teste com variância combinada. Confirmar pressupostos antes de reutilizar como referência de correção. |
| 148–150 | Com cálculo sem arredondamento intermediário: SQE=32/3, SQD=10/3 e F=9,6. O material apresenta aproximadamente 9,48 a partir de valores intermediários arredondados. |
| 161–163 | A inclinação é chamada de coeficiente de correlação, e a página 163 descreve o intercepto como “onde Y=0”, em conflito com a definição da página 161, que usa X=0. |

Também foram conferidos, como amostra: as frequências da tabela das páginas 49–51 (50 dados, frequências 6, 10, 13, 8, 5, 6 e 2); os cálculos da questão 7 da lista; e as 35 combinações do exemplo de permutação, com 2 casos tão ou mais extremos, confirmando 2/35. As conferências são cálculos locais desta análise, não gabaritos oficiais adicionais.

**Limitação da cópia local do projeto:** o RAG e o endpoint interno de chat estão presentes. Não foram localizados os endpoints, entidades ou regras implementadas de autorização/prática citados no pedido. A pasta `frontend` está vazia e o código Spring Boot disponível contém a classe inicial da aplicação. Antes da integração da prática, será necessário localizar a implementação ou especificação dessas regras, sem presumir que já existem nesta cópia nem criar um caminho que as contorne.

## Validação local e sequência após aprovação

`propostas/estatistica/validacao_mapa.json` registra a conferência do mapa com os métodos originais `AssuntoProcessor.paginas_por_assunto` e `validar_arquivo`, carregados isoladamente para não inicializar serviços. Resultado: 176 páginas reais, 166 mapeadas, dez exclusões explícitas, zero sobreposições, zero intervalos fora do documento e zero conflitos entre extração textual e visual. Isso valida a estrutura proposta; ainda não comprova chunks, recuperação ou respostas.

Após a aprovação explícita do mapa:

1. Instalar a versão aprovada em `app/rag/mapas/estatistica.py`, mantendo o fluxo `AssuntoProcessor` → `DocumentProcessor` → `ChunkProcessor` e os filtros existentes.
2. Processar e revisar uma amostra com fórmulas, tabela de frequência, gráficos e intervalos; preservar arquivo, página física, assunto, metadados documentais e páginas mescladas. Não misturar correções de revisão ao texto original sem identificar sua origem.
3. Conferir os chunks e a cobertura por assunto antes de persistir. Executar a auditoria e a ingestão pelo fluxo existente, depois testar perguntas com fontes reais e o comportamento de ausência de contexto.
4. Preparar o cadastro das avaliações com numeração, enunciados, subitens, alternativas, origens e situação do gabarito, mantendo pendentes as autorizações não comprovadas. A digitalização da questão 7 exige conferência visual: a camada de texto omite o valor 6; a imagem confirma [2, 4, 6, 8, 10].
5. Integrar prática somente pelos contratos aprovados do Spring Boot; resolver a ausência desses componentes nesta cópia antes de implementar. Manter FastAPI interno, filtros obrigatórios por disciplina, filtro por assunto quando solicitado, estado vazio e bloqueio de disciplina desabilitada.
6. Desenvolver a geração inédita e a correção didática em etapa própria, com matemática verificada, alternativas únicas, convenções explícitas, prevenção de repetição e identificação de conteúdo gerado por IA. Nenhuma questão deve aparecer como oficial por ter sido inspirada em prova.
7. Validar cada etapa antes de avançar: organização, referências, recuperação, autorização, disponibilidade, correção e experiência do aluno.

Até essa aprovação, esta entrega se limita às cópias verificadas, ao inventário, à análise dos conteúdos e ao mapa proposto.
