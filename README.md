# NEURON

Plataforma de apoio ao estudo desenvolvida no Projeto Extensionista 2. Reúne materiais acadêmicos, um Monitor Virtual com inteligência artificial e prática com questões em uma interface web responsiva.

O Monitor Virtual usa RAG (geração de respostas com consulta aos materiais): recupera trechos da disciplina e do assunto selecionados, elabora a explicação e apresenta as referências utilizadas. Quando não encontra conteúdo suficiente, informa essa limitação.

A implantação do piloto está documentada em [Publicação e operação](deploy/README.md), com os procedimentos de Docker Compose, persistência e verificações realizadas. O passo a passo abaixo descreve a execução local.

## Funcionalidades

- Acesso com autenticação por sessão e perfis de estudante e administrador.
- Cadastro de estudantes e gerenciamento administrativo de usuários (consulta, edição e exclusão com preservação do histórico).
- Consulta de períodos, disciplinas, assuntos e materiais acadêmicos.
- Monitor Virtual com referências de arquivo e página, contexto de conversa e histórico persistente por usuário, disciplina e assunto.
- Fontes agrupadas em **De onde veio esta explicação?**, com título, página e link para abrir o material quando disponíveis nos metadados.
- Fórmulas renderizadas com KaTeX em mensagens e exercícios, incluindo frações, potências, raízes, limites e integrais com notação matemática delimitada.
- Exemplos didáticos em tabelas e diagramas textuais, identificados como conteúdo criado pela IA e associados às fontes do conceito.
- Prática de Estatística com questões dos materiais e questões inéditas geradas por IA, correção explicada e conferência matemática nas famílias implementadas.
- Sistemas Digitais com 12 PDFs, Monitor Virtual e questões conceituais e contextualizadas de IA, com resolução em etapas. A lista e a prova ainda não foram fornecidas. Veja [a documentação](docs/SISTEMAS_DIGITAIS.md).
- Abertura dos materiais e das fontes disponíveis pelo servidor.
- Cálculo para Computação I no 2º período, com funções e limites na unidade 1 e derivadas na unidade 2; prática com filtros por regra e função, correções passo a passo e consulta à tabela de derivadas. Veja [a integração](docs/CALCULO_COMPUTACAO_I.md).
- Simulados de Cálculo I e II por assuntos selecionados, por unidade, final e segunda chamada, com correção ao finalizar.
- Cálculo para Computação II no 3º período: integrais de uma variável na primeira unidade, duplas e triplas diretas na segunda, tabela de integrais e simulados autorais. Funções de várias variáveis ficam como complemento opcional. Veja [a integração](docs/CALCULO_COMPUTACAO_II.md).
- Controle administrativo da disponibilidade de materiais para prática.
- Estrutura de Dados Avançada com questões conceituais e testes de mesa diretos ou contextualizados; Design de Artefatos Digitais com 27 questões contextualizadas e simulados por conteúdos escolhidos. Veja [a documentação](docs/PRATICA_ED_AVANCADA_DESIGN.md).
- Estrutura de Dados no 2º período, com dez PDFs, questões conceituais, lógica e testes de mesa em C; modos direto ou contextualizado, separados das questões originais da prova parcial. Veja [o guia da disciplina](neuron-ai/ESTRUTURA_DE_DADOS.md).
- Avaliação voluntária da plataforma por estudantes, com nota de 1 a 5, comentário opcional e possibilidade de atualizar a resposta.
- Consulta pública de avaliações em `/#avaliacoes`, com nome do aluno, nota, comentário, data no horário de Fortaleza, média e paginação de dez respostas. O formulário informa que a avaliação é pública; o envio exige conta de estudante autenticada.
- Interface adaptada a computador, tablet e celular.

O serviço de IA possui preparação de materiais para Estatística, Estrutura de Dados, Estrutura de Dados Avançada, Design de Artefatos Digitais, Projeto de Ideação de Software, Sistemas Digitais e Cálculo para Computação I e II. O catálogo web depende das migrations e dos materiais integrados ao banco; a existência de um corpus no serviço de IA não significa que todas as funcionalidades estejam disponíveis para aquela disciplina na interface.

## Arquitetura e tecnologias

```text
Navegador → React / Vite → Spring Boot → FastAPI / RAG → OpenRouter
                              │               │
                              └── PostgreSQL ──┘
                                    pgvector
```

| Componente | Tecnologias e responsabilidade |
| --- | --- |
| Interface | React, Vite, React Markdown, remark-math, KaTeX e estilos responsivos |
| API pública | Java, Spring Boot, Spring Security, JPA e Flyway; autenticação, permissões, catálogo e histórico |
| Serviço de IA | Python, FastAPI, LangChain, Sentence Transformers, SymPy e cliente OpenAI para acesso ao OpenRouter |
| Persistência | PostgreSQL para dados acadêmicos e conversas; pgvector para busca vetorial nos materiais |
| Verificação | JUnit/Spring Boot Test, Vitest/Testing Library e unittest |

O navegador consome a API Spring em `/api`. As rotas Python em `/internal/v1` são acessadas pelo servidor com o cabeçalho `X-Internal-Token`.

## Estrutura do projeto

```text
NEURON/
├── backend/demo/               # API Java, migrations e testes
├── frontend/                   # Interface React e testes
│   └── qa/                     # Prévia visual com dados fictícios
├── neuron-ai/
│   ├── app/api/                # Rotas internas e autenticação entre serviços
│   ├── app/rag/                # Extração, busca, embeddings e Monitor Virtual
│   ├── app/practice/           # Preparação e correção de questões
│   ├── materiais_academicos/   # Fontes acadêmicas e corpus preparado
│   ├── scripts/               # Preparação, integração e validação
│   ├── sql/                   # Estrutura do índice vetorial
│   └── test/                  # Testes Python
├── docs/                      # Documentação da integração e da interface
├── deploy/                    # Dockerfiles, Compose e documentação de publicação
└── requirements.txt           # Dependências Python da etapa inicial
```

## Executar localmente

Os exemplos abaixo usam PowerShell e partem da pasta `NEURON`. No VS Code, use **Arquivo → Abrir Pasta** e selecione a pasta `NEURON`, dentro de `Projeto Extensionista 2`.

### 1. Pré-requisitos

- Node.js e npm compatíveis com o Vite 8 usado pela interface.
- JDK 17 ou compatível. O código é compilado com alvo Java 17; outro JDK pode ser selecionado com `-PjavaVersion`, como nos exemplos com JDK 23 da documentação técnica.
- Python com suporte às dependências do projeto. O ambiente local de desenvolvimento utiliza Python 3.13.
- PostgreSQL com a extensão pgvector instalada.
- Credencial do OpenRouter para as funcionalidades que geram respostas ou processam páginas com modelo de visão.

O Gradle Wrapper está incluído em `backend/demo`; não é necessário instalar o Gradle separadamente.

### 2. Dependências

Crie o ambiente Python dentro de `neuron-ai`:

```powershell
python -m venv neuron-ai/.venv
& ./neuron-ai/.venv/Scripts/python.exe -m pip install -r requirements.txt
& ./neuron-ai/.venv/Scripts/python.exe -m pip install python-dotenv 'psycopg[binary]' openai httpx
```

O `requirements.txt` atual é da etapa inicial e não lista todas as dependências importadas pelo serviço integrado; o segundo comando complementa essa instalação.

Instale as dependências da interface:

```powershell
Set-Location frontend
npm.cmd install
Set-Location ..
```

Prepare as dependências Java com acesso à rede na primeira execução:

```powershell
Set-Location backend/demo
./gradlew.bat classes
Set-Location ../..
```

Se estiver usando outro JDK, acrescente o parâmetro correspondente, por exemplo `./gradlew.bat -PjavaVersion=23 classes`, e configure `JAVA_HOME` para esse JDK.

### 3. Configuração local

Crie um arquivo `.env` na raiz de `NEURON`, preenchendo os valores locais:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neuron
DB_USER=postgres
DB_PASSWORD=SUBSTITUA_PELA_SENHA_LOCAL
DB_URL=jdbc:postgresql://localhost:5432/neuron
AI_SERVICE_URL=http://127.0.0.1:8000
NEURON_INTERNAL_TOKEN=SUBSTITUA_POR_UM_TOKEN_ALEATORIO_LONGO
OPENROUTER_API_KEY=SUBSTITUA_PELA_SUA_CHAVE
```

O inicializador `scripts.servicos_local` carrega os arquivos `.env` de `neuron-ai` e da raiz. Evite definições conflitantes; o token interno precisa ser igual nos dois serviços. O Spring iniciado diretamente pelo Gradle recebe variáveis do ambiente, sem carregar automaticamente esses arquivos.

As opções `OPENROUTER_MODEL` e `OPENROUTER_VISION_MODEL` permitem configurar os modelos de texto e visão. O modelo de visão é necessário para a extração multimodal dos materiais que exigem esse processamento. Credenciais ficam nos arquivos locais ignorados pelo Git.

### 4. Banco de dados e materiais

Crie o banco `neuron` no PostgreSQL, caso ainda não exista. Aplique o SQL do índice vetorial com uma conta autorizada a criar a extensão:

```powershell
psql -h localhost -p 5432 -U postgres -d neuron -f neuron-ai/sql/001_chunk_documento.sql
```

Prepare as tabelas acadêmicas e o histórico pelo comando de migração:

```powershell
Set-Location neuron-ai
./.venv/Scripts/python.exe -B -m scripts.servicos_local migrar
```

Esse comando aceita a preparação de uma base vazia ou contendo somente a tabela inicial `chunk_documento`, além de bases já gerenciadas pelo Flyway. Uma base sem histórico de migrations e com outras tabelas exige revisão antes da migração.

O catálogo relacional e o índice vetorial são estruturas distintas. Para responder com fontes e oferecer prática, é necessário preparar e integrar os materiais; criar as tabelas não popula o corpus. Consulte os guias por disciplina na seção de documentação antes de executar os scripts de preparação, indexação e integração.

### 5. Iniciar os serviços

No VS Code, use **Terminal → Novo Terminal** para abrir três terminais PowerShell separados, cada um começando na pasta `NEURON`. Antes de iniciar, confirme que o PostgreSQL está em execução.

Os comandos abaixo usam diretamente o Python de `neuron-ai/.venv`; não é necessário ativar um ambiente virtual nem alterar a política de execução do PowerShell. Se existir também uma pasta `NEURON/.venv`, ela não é o ambiente usado por esses comandos.

```powershell
# Terminal 1: serviço de IA
Set-Location neuron-ai
./.venv/Scripts/python.exe -u -B -m scripts.servicos_local ia
```

```powershell
# Terminal 2: API Java
Set-Location neuron-ai
./.venv/Scripts/python.exe -B -m scripts.servicos_local backend
```

O inicializador Java usa o modo offline do Gradle, por isso as dependências devem estar disponíveis previamente. Ele seleciona o JDK a partir de `JAVA_HOME`, com alternativa local para JDK 23.

O inicializador de IA pré-carrega o Monitor e usa o modelo local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, com embeddings de 384 dimensões. Por padrão, ele procura o modelo em cache, em modo offline. Se o modelo ainda não estiver disponível, configure `HF_HUB_OFFLINE=0` e `TRANSFORMERS_OFFLINE=0` no `.env` para permitir o primeiro download. Aguarde a conclusão da inicialização antes de consultar o Monitor.

Para a interface, use o terceiro terminal, também começando na pasta `NEURON`:

```powershell
# Terminal 3: interface
Set-Location frontend
npm.cmd run dev
```

No Windows, `npm.cmd` evita o bloqueio do script `npm.ps1` pela política de execução do PowerShell. Deixe os serviços em execução e abra no navegador o endereço exibido pelo Vite.

Na IA, aguarde `Application startup complete` e a confirmação de que o Uvicorn está atendendo em `http://127.0.0.1:8000`. No Java, aguarde a confirmação de que o Tomcat iniciou na porta 8080 e a mensagem `Started DemoApplication`. A tarefa `bootRun` permanece em execução enquanto o servidor está ativo; não é necessário aguardar `BUILD SUCCESSFUL` para abrir a interface.

| Serviço | Endereço padrão |
| --- | --- |
| Interface | `http://127.0.0.1:5173` — confirme a porta informada pelo Vite |
| API Java | `http://127.0.0.1:8080` |
| Serviço de IA | `http://127.0.0.1:8000` |
| Documentação da API interna | `http://127.0.0.1:8000/docs` |
| Verificação HTTP da IA | `http://127.0.0.1:8000/health` |

O `/health` confirma que o serviço HTTP está ativo; não verifica a disponibilidade do banco ou do provedor de IA. O Vite encaminha `/api` para a API Java durante o desenvolvimento.

Para encerrar um serviço iniciado nesse terminal, pressione **Ctrl+C**. Antes de repetir um comando de inicialização, confira se já existe uma instância funcionando.

### 6. Primeiro acesso

Na instalação local, a tela inicial oferece **Explorar sem conta**. O visitante pode consultar disciplinas e materiais e conversar com o Monitor Virtual. Não pode administrar materiais, praticar questões nem avaliar a plataforma. Cada visita recebe uma sessão separada; o histórico é apagado ao sair ou na limpeza periódica após um dia. O inicializador habilita esse acesso somente no computador local. Ao iniciar o backend por outro método, ele permanece desabilitado até definir `NEURON_GUEST_ENABLED=true`.

Para criar uma conta de estudante, selecione **Criar uma conta** na tela de entrada e informe nome, email e senha. Após o cadastro, entre com os dados definidos. Administradores podem consultar, cadastrar, editar e excluir estudantes pela opção **Usuários**. A exclusão desativa o acesso e preserva conversas e avaliações. Consulte [Cadastro e gerenciamento de usuários](docs/USUARIOS.md) para as regras de acesso e validação.

Não há senha padrão. Para criar o administrador inicial em uma instalação nova, defina no `.env`, antes de iniciar o backend:

```dotenv
NEURON_BOOTSTRAP_ADMIN_EMAIL=SUBSTITUA_PELO_EMAIL_DO_ADMINISTRADOR
NEURON_BOOTSTRAP_ADMIN_PASSWORD=SUBSTITUA_POR_UMA_SENHA_COM_12_OU_MAIS_CARACTERES
```

O backend cria a conta se o e-mail ainda não existir. Após a criação, remova essas duas variáveis da configuração. O cadastro público cria somente estudantes; contas administrativas são protegidas contra edição e exclusão pelo gerenciamento de usuários.

Na implantação de produção documentada, o acesso de visitante está desativado e a entrada oferece login e cadastro de estudantes. A consulta de avaliações permanece pública.

#### Por que a opção Praticar não aparece?

Se o canto inferior esquerdo mostrar **Visitante**, o acesso foi feito por **Explorar sem conta**. Nesse perfil, o menu **Praticar** e o cartão **Praticar com IA** ficam ocultos, e a API também bloqueia as rotas de prática.

Para acessar as questões, saia da sessão de visitante e entre com uma conta de **Estudante** ou **Administrador**. Mesmo com uma conta autorizada, a disponibilidade depende da disciplina, dos materiais habilitados e da integração correspondente. O funcionamento do Monitor Virtual, por si só, não confirma que há questões disponíveis naquela seleção.

### 7. Problemas comuns ao iniciar

#### IA parada em Waiting for application startup

O serviço pré-carrega o modelo de embeddings antes de aceitar conexões. As mensagens `Carregando modelo de embeddings` e `Loading weights` indicam essa preparação. Aguarde a conclusão sem interromper o processo. Se o carregamento não avançar, confira as mensagens do terminal e a configuração de cache/download descrita na etapa 5.

#### Aborted! seguido de KeyboardInterrupt

O processo recebeu uma interrupção, geralmente por **Ctrl+C** ou pelo comando de parar do terminal. Esse registro isolado não identifica uma falha do modelo. Confira as mensagens anteriores à interrupção e verifique se já há uma instância ativa antes de iniciar novamente.

#### WinError 10048 na porta 8000

Outra aplicação já está usando a porta da IA. A nova tentativa pode carregar o modelo e mostrar `Application startup complete` antes de falhar ao abrir a porta; por isso, essa mensagem sozinha não confirma que a nova instância ficou disponível.

Abra `http://127.0.0.1:8000/health`. Se a resposta for a seguinte, há uma instância do serviço de IA respondendo e não é necessário iniciar outra:

```json
{"status":"ok","service":"neuron-ai"}
```

#### Port 8080 was already in use

Outra aplicação já está usando a porta da API Java. Se já houver um backend NEURON em execução, use essa instância. Para conferir a integração, abra a interface, entre ou escolha **Explorar sem conta** e verifique se as disciplinas carregam.

Para identificar os processos que usam as portas 8000 e 8080, execute no PowerShell:

```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :8080
```

Nas linhas de escuta (`LISTENING`), a última coluna informa o PID do processo, que pode ser consultado na aba **Detalhes** do Gerenciador de Tarefas. Se precisar reiniciar uma instância conhecida, encerre-a com **Ctrl+C** no terminal em que foi iniciada e só então execute o comando novamente.

#### Port 5173 is in use, trying another one...

O Vite tenta automaticamente a próxima porta disponível. Se mostrar `Local: http://127.0.0.1:5174/`, por exemplo, abra esse endereço. Isso não é uma falha de inicialização. Use a mesma porta para acessar a prévia em `/qa/preview.html`.

#### FutureWarning sobre get_sentence_embedding_dimension

O aviso informa que o método foi renomeado para `get_embedding_dimension`. Ele não impede o carregamento do modelo na versão atual. Confira as mensagens seguintes para saber se o serviço concluiu a inicialização ou encontrou outro erro.

## Testes e conferência visual

Execute cada grupo na pasta indicada:

```powershell
# Em frontend/
npm.cmd test -- --pool=threads --maxWorkers=1
npm.cmd run build
```

```powershell
# Em backend/demo/
./gradlew.bat test
# Com outro JDK, por exemplo: ./gradlew.bat -PjavaVersion=23 test
```

```powershell
# Em neuron-ai/, com o ambiente Python preparado
./.venv/Scripts/python.exe -B -m unittest discover -s test -p 'test_*.py' -v
```

A prévia `http://127.0.0.1:5173/qa/preview.html` permite conferir a interface com dados fictícios enquanto o Vite está ativo. Ela não acessa banco nem IA e não faz parte da entrada de produção. Veja [o roteiro de conferência visual](frontend/qa/README.md).

Os scripts de validação de integração são separados dos testes acima e podem depender de banco, corpus preparado e credenciais reais. Resultados e condições das validações anteriores estão documentados nos guias técnicos.

## Escopo e limitações atuais

- As conversas do Monitor são persistidas; as sessões de prática são temporárias e expiram, por padrão, em 60 minutos. O serviço de IA deve permanecer com um único worker para o estado atual da prática.
- A API pública de chat utiliza eventos SSE, mas entrega o texto após a geração completa; ainda não transmite cada token diretamente do provedor.
- A prática depende de materiais autorizados e das regras implementadas para cada disciplina; ela não está disponível automaticamente em todo o catálogo.
- A renderização matemática depende de notação delimitada. Mensagens antigas com divisões escritas usando `/` não são convertidas automaticamente em frações.
- A interface diferencia conteúdo acadêmico, questões inéditas de IA e observações produzidas pela IA. A presença de um gabarito não confirma sua autoria oficial.
- Monitoria humana, mensagens com monitores humanos, agendamentos, upload genérico e administração completa do catálogo estão fora do escopo atual.
- A configuração descrita neste passo a passo é de desenvolvimento local. O build da interface é gerado em `frontend/dist`. A implantação documentada usa Docker Compose e Caddy para servir a interface por HTTPS e encaminhar a API; banco e serviços internos ficam na rede Docker. Consulte [Publicação e operação](deploy/README.md).

## Documentação

- [Cadastro e gerenciamento de usuários](docs/USUARIOS.md)
- [Publicação e operação com Docker Compose](deploy/README.md)
- [Estrutura de Dados do 2º período](neuron-ai/ESTRUTURA_DE_DADOS.md)
- [Cálculo para Computação I: prática e simulados](docs/CALCULO_COMPUTACAO_I.md)
- [Cálculo para Computação II: integrais e simulados](docs/CALCULO_COMPUTACAO_II.md)
- [Prática de Estrutura de Dados Avançada e Design](docs/PRATICA_ED_AVANCADA_DESIGN.md)
- [Integração de Sistemas Digitais](docs/SISTEMAS_DIGITAIS.md)
- [Formatação matemática](docs/FORMATACAO_MATEMATICA_PUBLICADA.md)
- [Apresentação das fontes do Monitor](docs/FONTES_LEGIVEIS_PUBLICADAS.md)
- [Interface, responsividade, histórico e avaliação](docs/FRONTEND_E_HISTORICO.md)
- [Chat conversacional com RAG e contexto](docs/CHAT_CONVERSACIONAL_RAG.md)
- [Backend, segurança, prática e integração de Estatística](docs/BACKEND_ESTATISTICA.md)
- [Interface e prática de Estatística](docs/FRONTEND_ESTATISTICA.md)
- [Integração de Estrutura de Dados Avançada](docs/BACKEND_ED_AVANCADA.md)
- [Integração de Design de Artefatos Digitais](docs/BACKEND_DESIGN.md)
- [Integração de Projeto de Ideação de Software](docs/BACKEND_IDEACAO.md)
- [Monitor de Estatística](neuron-ai/MONITOR_ESTATISTICA.md)
- [Monitor de Estrutura de Dados Avançada](neuron-ai/MONITOR_ED_AVANCADA.md)
- [Monitor de Design de Artefatos Digitais](neuron-ai/MONITOR_DESIGN.md)
- [Monitor de Projeto de Ideação de Software](neuron-ai/MONITOR_IDEACAO.md)

Alguns documentos registram etapas anteriores do desenvolvimento. Para o comportamento atual, considere também os guias de integração mais recentes e o código dos serviços.
