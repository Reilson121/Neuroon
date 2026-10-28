# Projeto de Ideação de Software: backend e interface

A migration V6 cadastra a disciplina no terceiro período, os cinco assuntos e
os cinco PDFs originais. O catálogo React carrega esses dados pela API existente,
sem IDs fixos. A biblioteca filtra os materiais pelo assunto selecionado.

Os assuntos são Introdução, Lean Canvas, Histórias de Usuário, Mapa de Navegação
e Wireframe e Matriz CSD. A seleção é enviada ao Monitor Virtual; o backend
traduz os IDs para os slugs do RAG. As fontes incluem o ID do material para abrir
o PDF autenticado na página citada. As conversas utilizam o histórico existente.
A prática permanece indisponível porque não há avaliações autorizadas.

## Aplicar na base local

Na pasta `neuron-ai`, com o ambiente e o banco configurados:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.servicos_local migrar
.\.venv\Scripts\python.exe -B -m scripts.integrar_materiais_ideacao
```

A integração confere o corpus, os hashes dos originais e os assuntos antes de
vincular os materiais. Preserva os 217 IDs, textos, páginas e revisões acadêmicas;
reutiliza embeddings quando o texto já está indexado. A sincronização é limitada
aos arquivos da disciplina e confere as assinaturas das demais disciplinas.
Pode ser repetida. Não requer nova ingestão nem chamadas ao provedor de IA.

Inicie API, IA e interface conforme o README. Selecione o terceiro período e
Projeto de Ideação de Software na biblioteca ou no Monitor Virtual.

## Verificação

`IdeacaoApiTests`, `test_ideacao_materials.py` e `Ideacao.test.jsx` verificam o
catálogo, os vínculos dos 217 trechos, a autorização dos PDFs, os filtros, as
fontes, o histórico e a indisponibilidade de prática.

Com a API local iniciada, execute:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.validar_backend_ideacao
```

O script verifica o catálogo, os cinco PDFs e a busca filtrada nos cinco assuntos.
Cria uma conta temporária e a remove ao terminar. O relatório fica em
`saidas_testes/ideacao_validacao_backend.json`. A opção `--com-provedor` também
gera uma resposta pelo provedor configurado e pode consumir créditos.

## Conferência local em 28/10/2026

- Migration V6 aplicada; cinco materiais e cinco assuntos cadastrados.
- Os 217 trechos receberam os vínculos relacionais, sem novos embeddings,
  inserções ou remoções; as demais disciplinas foram preservadas.
- Três testes de materiais e o teste específico da interface aprovados.
  A interface compilou para produção.
- A API local conferiu o catálogo, a abertura autenticada dos cinco PDFs
  e a indisponibilidade de prática. A conta temporária foi removida.
- As primeiras execuções das suítes completas sofreram com disputa pelo cache
  do Gradle e tempo de espera ao iniciar workers da interface. Foram repetidas
  sem concorrência e com a interface executando os arquivos sequencialmente.

Na continuação da verificação, a suíte Java completa passou com 46 testes,
incluindo os seis `IdeacaoApiTests`. A suíte Python completa passou com 123 testes.
A busca com o modelo local, sem provedor externo, passou em quatro casos
selecionados (Lean Canvas, Histórias de Usuário, Mapa de Navegação e Matriz CSD).
A auditoria confirmou os 217 trechos no banco, com corpus compatível.
A suíte completa da interface passou com 20 testes em 7 arquivos ao executar
os arquivos sequencialmente, com um processo de teste por vez.
O pacote Java foi reconstruído e conferido; inclui a migration V6.
O script de aceitação local também passou pela API pública: catálogo com cinco
assuntos e cinco materiais, abertura autenticada dos PDFs, prática bloqueada e
busca filtrada nos cinco assuntos com IDs relacionais corretos. A conta temporária
foi removida. O relatório `ideacao_validacao_backend.json` registra essa validação;
`validacao_busca_ideacao_selecionados.json` traz os casos de busca selecionados.
A geração real foi autorizada explicitamente pelo usuário nesta conversa. A
pergunta sobre os nove blocos do Lean Canvas atravessou a API pública, o serviço
de IA e o OpenRouter. O teste confirmou a resposta, as fontes por SSE e o histórico,
e removeu a conta temporária ao terminar. A resposta trouxe os nove blocos na
ordem da página 8 da Aula 2, conferida visualmente no PDF original. A página 2
cita estruturar uma ideia e formular hipóteses, apoiando a explicação adicional.
As fontes [F1] e [F2] apontaram, respectivamente, para as páginas 8 e 2 do PDF.
O relatório `ideacao_validacao_backend.json` registra o resultado aprovado.
