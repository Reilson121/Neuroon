# Design de Artefatos Digitais: IA, backend e interface

A migration V5 cadastra a disciplina no terceiro período, seus nove assuntos
e nove PDFs (oito aulas e o complementar da Matriz CSD). Cada material pertence
ao assunto do corpus. Não habilita prática sem avaliações autorizadas.

O catálogo React recebe a disciplina pela API Spring existente, sem IDs fixos.
A seleção de assunto segue para o Monitor, que traduz os IDs para os slugs
usados pelo RAG. As fontes retornam `material_id`, permitindo abrir o PDF
autenticado na página citada; as conversas usam o histórico existente.

`design_corpus.preparar_material` verifica os originais e o consolidado antes
de vincular os trechos. Preserva IDs, texto, páginas e revisões acadêmicas.
Recusa origens divergentes, fontes revogadas e assuntos incompatíveis.
O indexador compartilhado atualiza metadados e colunas relacionais sem
recalcular embeddings quando o texto já está indexado. A integração verifica
as assinaturas das demais disciplinas e pode ser repetida.

## Aplicar na base local

Na pasta `neuron-ai`, com o ambiente existente e o `.env` local configurado:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.servicos_local migrar
.\.venv\Scripts\python.exe -B -m scripts.integrar_materiais_design
```

Em terminais separados, iniciar `scripts.servicos_local backend` e
`scripts.servicos_local ia` com o mesmo Python. Em `frontend`, iniciar
`npm run dev`. Na interface, selecionar o terceiro período e Design de
Artefatos Digitais. Os assuntos filtram o Monitor e a biblioteca.

## Validação

Os testes `DesignApiTests`, `test_design_materials.py` e `Design.test.jsx`
cobrem tradução dos IDs, acesso aos PDFs, bloqueio da prática sem materiais,
preservação dos 363 trechos e envio da pergunta com assunto e fontes na interface.

Com os serviços locais iniciados:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.validar_backend_design
.\.venv\Scripts\python.exe -B -m scripts.validar_backend_design --com-provedor
```

O primeiro valida o catálogo, os nove PDFs e a recuperação em todos os assuntos.
O segundo também envia uma pergunta sobre Design Thinking ao provedor
configurado e confere fontes, SSE e histórico; pode consumir créditos.
A conta temporária e seu histórico são removidos ao encerrar.
Relatórios ficam em `saidas_testes/design_integracao_materiais.json` e
`saidas_testes/design_validacao_backend.json`.

## Verificação local em 28/10/2026

- Os 363 trechos receberam os vínculos dos nove materiais, sem inserir,
  remover ou recalcular embeddings. As demais disciplinas foram preservadas.
- A repetição não alterou nenhum registro; o relatório separado está em
  `saidas_testes/design_integracao_repeticao.json`.
- Suíte completa do backend aprovada e pacote Java reconstruído. Após incluir
  a cobertura específica de histórico, os seis testes `DesignApiTests` passaram.
- 120 testes da IA e 19 testes da interface aprovados; interface compilada.
- A API local conferiu o catálogo e a abertura autenticada dos nove PDFs.
  A busca real passou nos nove assuntos, com IDs relacionais das fontes
  conferidos; a conta temporária foi removida ao final.
  O histórico de Design, as fontes com ID do material e a continuação no mesmo
  assunto foram conferidos com resposta de teste local, sem provedor externo.
- Com autorização do usuário, uma pergunta real sobre as cinco etapas do
  Design Thinking foi respondida pelo OpenRouter. A resposta citou a Aula 8,
  páginas 10, 8 e 9; os trechos foram conferidos contra o corpus. A API entregou
  resposta e fontes via SSE e reabriu a conversa pelo histórico. O relatório
  `saidas_testes/design_validacao_backend.json` foi aprovado e confirma a
  remoção da conta temporária.
