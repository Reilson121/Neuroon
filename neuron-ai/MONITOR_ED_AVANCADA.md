# Monitor Virtual — Estrutura de Dados Avançada

Fluxo implementado: pergunta → embedding local → Top-K no pgvector,
filtrado por disciplina e assunto opcional → cadeia LangChain → modelo
já configurado via OpenRouter → resposta com referências e metadados reais.

## Estado da validação

- Confirmado: pgvector 0.8.5 e coluna de embeddings vector(384).
- JSON atual das Aulas 0, 1 e 2: 167 chunks após mesclagem de páginas curtas.
- Auditoria executada pelo usuário: 33 chunks extras, 27 textos divergentes,
  30 divergências de metadados e nenhum chunk ausente. Índice desatualizado confirmado.
- Sincronização executada e conferida: banco com 167 chunks, zero ausências,
  extras ou divergências de textos/metadados. Foram removidos 33 IDs obsoletos,
  atualizados 30 registros e recalculados 27 embeddings.
- Recuperação real: assunto esperado em primeiro lugar nas sete perguntas de
  `scripts.test_busca`; filtro por assunto validado para Splay.
- Execução direta pelo agente: fila de prioridade respondeu com referências
  às páginas 3–4, 6 e 112 da Aula 2, conferidas contra os trechos processados.
- Execução direta pelo agente: capital da França retornou `sem_contexto`,
  sem fontes; esse caminho retorna antes da chamada ao modelo.
- Página 131 de Aula_2.pdf ausente dos chunks atuais; nenhum mapa foi alterado.
- Os 30 testes unitários passaram com dependências simuladas. A execução real
  usa o carregamento de configuração existente do serviço, sem exibir segredos.
- A validação adicional de respostas em seis temas é executada por
  `scripts.validar_respostas_ed_avancada`, com relatório em
  `saidas_testes/validacao_respostas_ed_avancada.json`.
- Lote real adicional: Gini, Trie, Splay e Red-Black tiveram respostas conferidas
  contra os trechos citados. A comparação BST/Heap também foi conferida, após
  reprocessar localmente a saída real para remover um parágrafo sem referência.
  Esse reprocessamento não gerou uma nova resposta nem uma nova busca.
- Diagnóstico inicial: a pergunta sobre rotação zig-zag em AVL retornava fallback
  com Top-K 5. O procedimento está na página 90, mas a busca inicial traz as páginas
  93, 87, 92, 86 e 107. O diagnóstico Top-10 também não recuperou a página 90.
  Não se deve confundir assunto correto no topo com contexto suficiente.
  A comparação posterior com os mesmos filtros e Top-K 5 recuperou a página 90
  em terceiro lugar com a consulta `rotação zig-zag esquerda-direita`.
- Reformulação implementada: se o modelo indicar contexto insuficiente, pode
  sugerir uma consulta curta; a aplicação refaz a busca mantendo a pergunta
  original, disciplina, assunto e Top-K. São permitidas até duas reformulações.
  Consultas repetidas/inválidas e falhas de geração encerram a tentativa.
  Sem contexto acima do limiar, não há chamada ao modelo.
- Validação real da reformulação concluída em 27/10/2026, após autorização
  explícita do usuário para envio ao OpenRouter. A primeira chamada indicou
  contexto insuficiente e sugeriu `rotação dupla esquerda-direita AVL`.
  A segunda busca trouxe as páginas 89, 88, 93, 91 e 90; a resposta citou
  as páginas 90 e 93. Foram duas chamadas ao modelo, com uma reformulação.
- Explicação do caso esquerda-direita, sequência das rotações e exemplo
  30/10/20 conferidos contra os trechos citados. Os seis casos do relatório
  adicional estão aprovados; somados ao teste anterior de fila de prioridade,
  há respostas conferidas em sete temas e um teste de fallback fora da disciplina.
- O RAG básico está validado nessa amostra. Isso não garante cobertura de toda
  pergunta possível. Top-K e critério final de suficiência permanecem em aberto.

## Executar no PowerShell

```powershell
Set-Location 'C:\Projeto Extensionista 2\NEURON\neuron-ai'
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ed_avancada --verificar-base
```

A execução normal usa o mecanismo de configuração já existente no serviço.
Nenhum comando imprime senhas, chaves ou o conteúdo do `.env`.
A auditoria é somente para leitura. Havendo divergência, o comando retorna 2,
interrompe o fluxo e não faz reingestão nem modifica o índice.

Para corrigir a divergência confirmada usando o JSON já processado:

```powershell
& '.\.venv\Scripts\python.exe' -B -m scripts.sincronizar_ed_avancada
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ed_avancada --verificar-base
```

A sincronização recalcula somente os embeddings dos textos alterados. Atualiza
conteúdos/metadados e remove IDs obsoletos em uma única transação. Mantém colunas
relacionais e campos extras dos metadados. Não reprocessa PDFs nem chama o LLM.
Faz uma conferência antes do commit; erros de aplicação provocam rollback.
Rejeita arquivos fora do conjunto processado ou IDs ausentes. Uma trava breve
impede escritas concorrentes na tabela durante a aplicação; o cálculo dos
embeddings ocorre antes dessa trava. Repetir o comando com a base compatível
não altera dados nem recalcula embeddings.

Depois que a base estiver compatível, validar a recuperação:

```powershell
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ed_avancada --somente-busca 'O que é uma fila de prioridade?'
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ed_avancada --somente-busca --assunto arvore_splay 'Como funciona uma árvore splay?'
```

Depois, testar respostas (cada comando pode consumir créditos no OpenRouter):

```powershell
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ed_avancada 'O que é uma fila de prioridade?'
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ed_avancada 'Qual é a capital da França?'
```

Verificar manualmente se a primeira resposta está apoiada nas páginas citadas
e se a segunda retorna fallback sem fontes. Repetir com AVL, trie, red-black,
splay, ordenação e uma pergunta sem cobertura nos materiais, antes de considerar
a disciplina validada para o RAG básico.

## Fontes e fallback

O modelo retorna JSON com `suficiente` e `resposta`. A aplicação exige citações
como `[F1]` em cada parágrafo, rejeita referências que não vieram da busca e
constrói a lista de fontes a partir do banco. Páginas mescladas são preservadas.
Blocos sem referências são descartados, preservando somente os blocos citados;
isso não garante que cada afirmação de um bloco esteja semanticamente correta.
JSON inválido, geração truncada ou referências inválidas produzem uma mensagem
de falha de geração com fontes vazias. Contexto vazio ou insuficiente produz
a mensagem de ausência de informação. Falhas de conexão/configuração
continuam sendo erros, não são tratadas como ausência de conteúdo acadêmico.

A chamada ao modelo desativa raciocínio opcional, seguindo o padrão já usado
pelo processador visual. O limite permanece 1800 tokens. Geração incompleta
tem motivo próprio (`geracao_incompleta`), distinto de ausência de contexto.
Referência: [controle de raciocínio no OpenRouter](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens).

O limiar 0.25 foi herdado da demo e é **experimental**, ajustável pelo argumento
`--similaridade-minima`; Top-K padrão 5 também é provisório. Nenhum critério final
de suficiência foi decidido. Similaridade e citações existentes não garantem
correção semântica: a conferência com os PDFs continua necessária.

A cadeia usa os componentes de LangChain já instalados e o SDK existente.
O JSON é validado na aplicação; não pressupõe suporte a JSON Schema no provedor.
Referência: [saídas estruturadas no OpenRouter](https://openrouter.ai/docs/guides/features/structured-outputs).

O endpoint interno `POST /internal/v1/chat` foi implementado com retorno JSON;
o contrato e os testes estão documentados em `API_CHAT_INTERNO.md`.
Integração com Spring Boot, SSE, histórico e frontend adicionada em 28/10/2026:
consulte `../docs/BACKEND_ED_AVANCADA.md`. A migration V4 cadastra a disciplina,
14 assuntos e três aulas; o índice passa a obedecer às permissões relacionais.
Prática segue indisponível até haver listas/provas elegíveis. LangGraph continua
como etapa posterior. Não houve alterações na extração ou nos mapas.

## Testes locais

### Correção de recuperação de definições curtas — 28/10/2026

As perguntas `o que uma pilha?` e `o que sao pilhas?`, filtradas por
`revisao_estruturas_em_c`, recuperavam corretamente a página 14 da Aula 0 em
primeiro lugar. Porém, os cossenos 0,1986 e 0,1970 ficavam abaixo do limiar
experimental 0,25. Todos os trechos eram descartados antes da chamada ao LLM,
produzindo `sem_contexto`. Não era ausência da definição nem problema de login.

ED agora usa a busca híbrida existente, mantendo permissões e filtros de
disciplina/assunto. A consulta lexical reconhece variantes controladas como
pilha/pilhas; pergunta original, embedding, textos e IDs do corpus permanecem
preservados. Evidência lexical permite ao modelo avaliar a definição mesmo com
cosseno baixo, usando a regra já existente de cobertura lexical. O modelo
continua obrigado a justificar suficiência e apresentar fontes.

106 testes passaram. Validação real das duas perguntas devolveu a definição
LIFO com referência à página 14. Heap e rotação AVL também responderam com
fontes; uma pergunta sobre a capital da França continuou em `sem_contexto`,
sem fontes. Relatório: `saidas_testes/ed_avancada_correcao_busca_pilhas.json`.
Esse teste de AVL verifica recuperação/resposta com referências, sem garantir
formatação completa de exemplos de código na saída.

```powershell
& '.\.venv\Scripts\python.exe' -B -m unittest discover -s test -p 'test_*.py' -v
```
