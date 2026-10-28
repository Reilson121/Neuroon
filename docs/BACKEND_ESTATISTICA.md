# Backend de Estatística

## Arquitetura e execução

Spring Boot é a única API pública. Autentica, controla permissões, valida disciplina/assunto e chama FastAPI pelo AiClient. FastAPI reutiliza o RAG e PostgreSQL/pgvector existentes. Nenhum segredo do banco ou OpenRouter deve ir ao navegador.

O .env ignorado pelo Git, na raiz NEURON, contém as configurações locais: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, OPENROUTER_API_KEY, os modelos existentes e NEURON_INTERNAL_TOKEN. O inicializador deriva DB_URL para o Spring. Valores não são publicados aqui.

Na pasta NEURON/neuron-ai, em terminais separados:

    .\.venv\Scripts\python.exe -B -m scripts.servicos_local ia
    .\.venv\Scripts\python.exe -B -m scripts.servicos_local backend

Spring escuta em 127.0.0.1:8080; FastAPI em 127.0.0.1:8000. Python usa um worker porque as sessões são temporárias. O inicializador encontra o JDK configurado; neste ambiente, JDK 23 com bytecode Java 17.

O inicializador da IA carrega o Monitor existente antes de aceitar chamadas, evitando que a primeira consulta do estudante pague o tempo de importação do modelo local. Aguarde a mensagem Application startup complete. Para desenvolvimento sem esse carregamento, configurar NEURON_PRELOAD_MONITOR=0. O carregamento não envia perguntas ao OpenRouter.

Flyway gerencia migrations. A preparação inicial usa scripts.servicos_local migrar; baseline zero só é permitido para a base contendo exclusivamente chunk_documento. Bases desconhecidas exigem revisão. Iniciar Spring posteriormente valida e aplica apenas migrations pendentes.

Não há senha padrão. Para criar o administrador inicial, fornecer NEURON_BOOTSTRAP_ADMIN_EMAIL e NEURON_BOOTSTRAP_ADMIN_PASSWORD ao iniciar o backend; a senha deve ter pelo menos 12 caracteres. Retirar essas variáveis após criar a conta. Contas da aceitação HTTP são aleatórias e removidas no final.

## API pública

Prefixo /api/v1. Autenticação por sessão HttpOnly, SameSite=Lax e CSRF. Antes de POST/PUT/DELETE, obter /auth/csrf e enviar o token no cabeçalho retornado. Após login, obter novo token. Manter cookies nas chamadas. Em publicação HTTPS, configurar NEURON_SECURE_COOKIE=true.

| Método | Caminho | Finalidade |
|---|---|---|
| GET | /auth/csrf | Token CSRF |
| POST | /auth/login | Entrar com email e senha |
| GET | /auth/me | Usuário autenticado |
| POST | /auth/logout | Invalidar sessão, retorno 204 |
| GET | /periodos | Períodos ativos |
| GET | /periodos/{id}/disciplinas | Disciplinas do período |
| GET | /disciplinas/{id} | Detalhe da disciplina |
| GET | /disciplinas/{id}/assuntos | Assuntos na ordem aprovada |
| GET | /disciplinas/{id}/materiais?assuntoId=... | Metadados dos materiais |
| POST | /monitor/chat | Consulta ao Monitor via SSE |
| GET | /monitor/conversas?disciplinaId=...&assuntoId=... | Conversas do usuário no contexto selecionado |
| GET | /monitor/conversas/{id} | Reabrir mensagens e referências da própria conversa |
| POST | /pratica/sessoes | Preparar questões |
| POST | /pratica/sessoes/{id}/respostas | Corrigir resposta |
| PUT | /admin/materiais/{id} | Atualizar flags e sincronizar índice |
| DELETE | /admin/materiais/{id} | Desativar e limpar índice |

Administração exige perfil ADMINISTRADOR, revalidado no banco. A entrega concentra-se nos materiais preparados de Estatística; não implementa upload genérico, cadastro público de usuários nem administração completa das demais entidades.

## Contrato da prática

Sessão: disciplinaId obrigatório, assuntoId opcional, origem LISTA/PROVA/MISTO, modo CADASTRADAS/GERADAS_IA, quantidade obrigatória de 1 a 10 e revisarVistas opcional. Padrões: MISTO, CADASTRADAS e false.

Com questões: HTTP 201, sessaoId, estado DISPONIVEL, mensagem e questoes. Cada questão tem id, enunciado, alternativas A–E, conceito, origem, fontes, aviso, fingerprint e visualizacao opcional. Não expõe gabarito, cálculo privado ou resolução antes da resposta. Visualizações fornecem dados para barras ou dispersão.

Sem questões: HTTP 200, estado SEM_QUESTOES e lista vazia. Não é falha técnica. Disciplina sem prática: HTTP 409, codigo DISCIPLINA_SEM_PROVA.

Correção recebe questaoId e alternativa A–E. Retorna correto, alternativaCorreta, conceito, formula, substituicao, calculos, resolucao, errosComuns, dica, resolucaoGeradaPorIa, origemGabarito, aviso e fontes. Campos matemáticos podem ser nulos em questões conceituais.

Fontes: materialId, tituloMaterial, arquivo, pagina e numeroQuestao. Página do DOCX pode ser nula. IDs são consultados pela API; não presumir valores fixos.

Reenviar a mesma alternativa retorna a mesma correção; tentar trocar resposta já corrigida retorna 409. Sessões pertencem ao usuário, expiram em 60 minutos e não são persistidas; ausência/expiração retorna 404. Revogação invalida correções de sessões existentes. Limite padrão de 30 requisições por minuto por usuário e operação, configurável em neuron.rate-limit.por-minuto.

Os contextos narrativos são validados em quantidade, formato e ausência de novos dados/condições. Uma saída inválida permite somente uma tentativa adicional de reparo pelo modelo; persistindo o erro, a sessão retorna indisponibilidade. O reparo não altera os cálculos validados nem cria questões para assuntos sem referências.

PUT administrativo recebe quatro booleanos: ativo, fonteMonitorVirtual, disponivelParaPratica e autorizacaoProfessor. Não presume autorização pelo simples cadastro do arquivo. Se a indexação falhar, a disponibilidade fica bloqueada até uma nova sincronização bem-sucedida.

## Monitor e serviço interno

POST /monitor/chat recebe disciplinaId, assuntoId opcional, pergunta de até 4000 caracteres e threadId opcional. Spring traduz os IDs para slugs do RAG. Eventos SSE: status, token, sources, done ou error. Nesta versão, token entrega o texto completo após a geração; não há streaming de tokens do provedor.

O histórico persistente do Monitor foi preservado e incluído nesta validação por autorização do usuário em 28/10/2026. A migration V3 cria conversa_monitor e mensagem_monitor. O evento done devolve o threadId salvo; enviá-lo nas perguntas seguintes mantém a conversa. Mensagens e fontes podem ser reabertas após novo login. Somente o dono acessa a conversa, e a continuação exige a mesma disciplina e o mesmo assunto. A listagem sem assuntoId retorna conversas gerais; com assuntoId, retorna as desse assunto. Cada conversa aceita até 200 mensagens. As sessões de prática continuam temporárias.

O histórico organiza e reabre mensagens; agora suas oito mensagens mais recentes também contextualizam continuações, conforme `CHAT_CONVERSACIONAL_RAG.md`. Cada resposta refaz a recuperação e respeita as permissões atuais dos materiais.

As fontes preservam arquivo, página, páginas mescladas, assunto, IDs e revisões de IA. A interface deve mostrar as referências e distinguir observações de IA de conteúdo oficial.

Rotas internas /internal/v1/chat, /internal/v1/practice/questions, /internal/v1/practice/answers e /internal/v1/materials/* exigem X-Internal-Token. O navegador não deve acessá-las. Indexação recebe apenas material_id, nunca caminhos arbitrários, e aceita somente os três materiais previamente inventariados de Estatística.

Erros públicos têm status, codigo e mensagem controlados pelo Spring. Segredos e mensagens externas não são refletidos. Falhas desconhecidas de IA retornam 503; conflitos conhecidos permanecem 404/409/429 conforme o caso.

## Testes e evidências

Na pasta NEURON/backend/demo:

    $env:JAVA_HOME='C:\Program Files\Java\jdk-23'
    .\gradlew.bat -PjavaVersion=23 test bootJar --offline

Na pasta NEURON/neuron-ai:

    .\.venv\Scripts\python.exe -B -m unittest discover -s test -p 'test_*.py' -v
    .\.venv\Scripts\python.exe -B -m scripts.integrar_materiais_estatistica
    .\.venv\Scripts\python.exe -B -m scripts.validar_estatistica
    .\.venv\Scripts\python.exe -B -m scripts.validar_backend_estatistica --com-provedor

A aceitação HTTP exige os dois serviços iniciados e o banco local de desenvolvimento. Altera permissões temporariamente, restaurando-as no finally, e remove suas próprias contas, conversas, mensagens e dados temporários. Não executar em produção nem simultaneamente ao uso por estudantes. --com-provedor chama o OpenRouter autorizado e usa créditos; sem a opção, testa apenas fluxos locais.

O relatório neuron-ai/saidas_testes/estatistica_validacao_backend.json registra os cenários aprovados e amostras geradas. O frontend do protótipo foi integrado posteriormente e validado com o backend real; resultados e inicialização estão em [FRONTEND_ESTATISTICA.md](FRONTEND_ESTATISTICA.md).

## Resultado verificado em 28/10/2026

- 27 testes do Spring, 100 testes de IA e 24 cenários HTTP aprovados.
- Recuperação conferida nos 31 assuntos; 193 chunks teóricos e 15 registros de origem das avaliações preservados.
- Cinco questões geradas no fluxo real tiveram respostas e unicidade da alternativa correta conferidas por cálculo independente.
- Histórico validado para persistência das perguntas, respostas e fontes, continuação, isolamento entre usuários e reabertura após novo login. Recusas por falta de contexto permanecem sem fontes inventadas.
- Contas, conversas e demais dados temporários dos testes removidos; permissões restauradas e demais disciplinas preservadas.

Consolidação: neuron-ai/saidas_testes/estatistica_validacao_final.json. A validação usou saída de build isolada em build-estatistica para evitar colisão com outra tarefa; não criou uma implementação paralela do backend. O hash do pacote efetivamente testado está em estatistica_pacote_validado.json.
