# Estrutura de Dados Avançada: backend, IA e interface

A disciplina usa o núcleo existente dos PDFs de modelagem e classes:
`Periodo → Disciplina → Assunto/Material`, com API pública no Spring Boot,
serviço interno FastAPI e PostgreSQL/pgvector. Não há outro backend paralelo.

## Conteúdo e integração

- Migration V4: disciplina no 3º período, 14 assuntos na ordem das aulas e os
  três materiais `Aula_0.pdf`, `Aula_1.pdf` e `Aula_2.pdf`.
- Os 167 chunks do corpus existente mantêm texto, identificador, página,
  páginas mescladas e metadados de extração. Recebem os IDs relacionais do
  período, disciplina, assunto e material.
- Inventário SHA-256 dos três originais e do corpus: arquivos alterados
  precisam de nova conferência antes da indexação.
- Indexação por material reutiliza o sincronizador transacional existente.
  A compatibilidade com aulas legadas sem `tipo_material` evita tentar
  reinserir IDs existentes ou recalcular embeddings desnecessariamente.
- A busca do Monitor respeita o cadastro atual: material, disciplina,
  período e assunto precisam estar ativos; a fonte precisa estar habilitada.
  Os demais filtros e a reformulação do RAG foram preservados.
- Busca híbrida combina similaridade e evidência lexical. Variantes controladas
  de singular/plural (como pilha/pilhas) entram somente na consulta lexical;
  o embedding e a pergunta enviada ao modelo continuam originais. Isso evita
  descartar definições explícitas dos slides por cosseno abaixo de 0,25.
- O frontend React em `frontend/`, derivado do protótipo, recebe a disciplina
  pela API. Não utiliza IDs fixos nem acessa diretamente o serviço de IA.
  O histórico existente também funciona para esta disciplina.

Não foram encontrados materiais separados de listas/provas autorizadas para ED.
O indicador `possui_prova` começa em `false`; não afirma que a disciplina é
avaliada por projetos. A prática retorna `409 DISCIPLINA_SEM_PROVA` até que o
cadastro e materiais elegíveis sejam preparados. Os slides não são convertidos
em provas e nenhum gabarito foi presumido.

## Abertura de materiais

`GET /api/v1/materiais/{id}/arquivo` exige conta ativa e material/contexto ativos.
O backend resolve a referência cadastrada dentro de uma raiz configurada,
valida o caminho real (inclusive links simbólicos) e bloqueia saída dessa pasta.
Não recebe caminhos do navegador nem revela caminhos locais no catálogo.

PDFs abrem no navegador; DOCX/PPTX são baixados. Respostas têm `Cache-Control:
no-store`. Fontes do chat com `material_id` incluem um link para o arquivo e
a página citada. `arquivoDisponivel` no catálogo indica uma referência local
de formato suportado; a existência física e as permissões são verificadas na
abertura.

Ao iniciar pelo diretório `backend/demo`, a raiz padrão é
`../../neuron-ai/materiais_academicos`. Em outra instalação configure
`NEURON_MATERIALS_ROOT` com o caminho absoluto. A publicação do frontend deve
encaminhar `/api` para o Spring, como faz o proxy de desenvolvimento do Vite.

## Preparar e executar localmente

Na pasta `neuron-ai`, usando o ambiente Python existente:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.servicos_local migrar
.\.venv\Scripts\python.exe -B -m scripts.integrar_materiais_ed_avancada
```

O segundo comando requer as variáveis do banco carregadas no ambiente ou
o `.env` existente da raiz NEURON. Não copie segredos para o frontend.
O script recusa materiais fora do inventário, preserva outras disciplinas e
registra o resultado em `saidas_testes/ed_avancada_integracao_materiais.json`.
Reexecutar não deve alterar conteúdo nem recalcular embeddings.

Em terminais separados, na mesma pasta:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.servicos_local backend
.\.venv\Scripts\python.exe -B -m scripts.servicos_local ia
```

Em `frontend`, executar `npm run dev`. Usar uma conta já cadastrada pela
administração. O serviço de IA deve terminar o carregamento antes do chat.

## Verificação

```text
backend/demo: gradlew.bat -PjavaVersion=23 test bootJar --offline
neuron-ai: .\.venv\Scripts\python.exe -B -m unittest discover -s test -p 'test_*.py' -v
frontend: npm test -- --pool=threads --maxWorkers=1
frontend: npm run build
```

Com os serviços iniciados, em `neuron-ai`:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.validar_backend_ed_avancada --com-provedor
```

A aceitação cria e remove sua própria conta e histórico. Verifica catálogo,
abertura dos PDFs, filtros reais nos 14 assuntos e bloqueio da prática. Com
`--com-provedor`, envia uma pergunta sobre heap ao modelo configurado, consome
créditos e verifica SSE, fontes e reabertura do histórico. O relatório é salvo
em `saidas_testes/ed_avancada_validacao_backend.json`. Executar somente na base
local de desenvolvimento. Os testes de backend também cobrem bloqueio de
acesso anônimo, material desativado, caminho externo e assunto incompatível.

Limites existentes preservados: o SSE entrega o texto após a geração completa;
o histórico recente agora participa da conversa, conforme `CHAT_CONVERSACIONAL_RAG.md`.
Respostas da IA devem continuar sendo conferidas contra as fontes.

## Resultado local em 28/10/2026

- Migration V4 aplicada e 167 trechos vinculados (18 + 24 + 125), sem inserir,
  remover ou recalcular embeddings. Assinaturas das outras disciplinas iguais.
- Repetição da integração: zero alterações em todos os materiais.
- 32 testes do backend, 103 testes da IA e 13 testes da interface aprovados.
  Os 17 testes de auditoria/sincronização foram repetidos após a adaptação
  para os trechos legados e passaram. Pacote Java e interface compilados.
- Aceitação HTTP real aprovada: catálogo, três PDFs, bloqueio da prática,
  recuperação com filtro nos 14 assuntos e uma pergunta real ao provedor.
- A resposta sobre fila de prioridade/heap apresentou fontes da Aula 2,
  páginas 4 (mesclada com 3), 6 e 9, e foi reaberta pelo histórico.
- A conta e o histórico temporários do teste foram removidos.

Esses resultados validam a integração e a amostra de resposta, sem garantir
correção acadêmica de toda pergunta possível.
