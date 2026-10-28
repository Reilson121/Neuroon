# Monitor Virtual - Projeto de Ideação de Software

As cinco aulas do período 03 estão preparadas para o RAG compartilhado do
NEURON. Os cinco PDFs contêm 180 páginas, divididas em 217 chunks com fontes
que identificam disciplina, assunto, aula, arquivo e página física do PDF.
Alguns slides têm numeração impressa diferente da posição no arquivo; as
citações do monitor usam a posição física, contada a partir de 1.

## Materiais e processamento

| Aula | Assunto aceito pela API | Páginas |
| --- | --- | ---: |
| 01 - Introdução | `introducao` | 67 |
| 02 - Lean Canvas | `lean_canvas` | 43 |
| 03 - Histórias de Usuário | `historias_de_usuario` | 12 |
| 04 - Mapa de Navegação e Wireframe | `mapa_de_navegacao_e_wireframe` | 38 |
| 05 - Matriz CSD | `matriz_csd` | 20 |

Quatro PDFs são compostos por imagens. A ingestão usa o modelo visual já
configurado no OpenRouter para 170 páginas e extração textual para as outras
10. Os quadros das páginas 3 e 4 de Histórias de Usuário também são visuais:
recuperar apenas o título descartaria o conteúdo desses quadros.

O envio dos cinco PDFs e das perguntas de teste ao OpenRouter foi autorizado
explicitamente pelo usuário nesta conversa em 27/10/2026. Novas execuções
de ingestão ou de validação com respostas podem consumir créditos.

Os resultados originais ficam em
`saidas_testes/ideacao_aula_XX_pipeline_completa.json`, e a ingestão mantém
checkpoints por página. Retomar usa o progresso salvo; uma saída completa
válida não é enviada novamente. A troca de PDF ou modelo invalida o checkpoint.
Extrações vazias ou interrompidas não são aceitas como páginas concluídas.

Seis páginas receberam correções locais conferidas nas imagens: remoção de
descrições decorativas das capas, correção do título EMENTA e do verbo
Substituir na técnica SCAMPER e preservação dos nove estados de interface
em uma única lista, sem descrições repetidas da barra lateral. As revisões ficam em
`app/rag/mapas/ideacao_revisoes.json`, acompanhadas do hash do PDF e do texto
anterior. Os arquivos de ingestão originais são preservados.

O consolidado é
`saidas_testes/projeto_de_ideacao_de_software_completa.json`. A preparação
verifica cobertura, identidade e conteúdo de todas as páginas e gera IDs
determinísticos. O manifesto contém os hashes dos PDFs, das extrações e das
revisões. O monitor e o indexador recusam um consolidado desatualizado.

## Execução

Na pasta `C:\Projeto Extensionista 2\NEURON\neuron-ai`:

```powershell
# Somente para a primeira ingestão ou para retomar uma execução interrompida.
# Envia páginas visuais ao OpenRouter; até três processos independentes.
& '.\.venv\Scripts\python.exe' -B -m scripts.ingerir_aula_ideacao todas --processos 3

# Consolidação local, sem chamadas externas.
& '.\.venv\Scripts\python.exe' -B -m scripts.preparar_ideacao

# Reutiliza o modelo de embeddings local, sem consultar o Hugging Face.
$env:HF_HUB_OFFLINE = '1'
& '.\.venv\Scripts\python.exe' -B -m scripts.indexar_ideacao
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ideacao --verificar-base
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ideacao --somente-busca 'Quais são os nove blocos do Lean Canvas?'

# Gera resposta via OpenRouter com citações.
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_ideacao 'Qual é a estrutura de uma história de usuário?' --assunto historias_de_usuario
```

O modo offline do Hugging Face exige que o modelo de embeddings já esteja
armazenado no computador, como nesta instalação. Em uma instalação nova,
baixe o modelo antes de ativar esse modo.

A indexação reutiliza a sincronização transacional existente: insere IDs
ausentes, atualiza divergências e remove IDs obsoletos somente no conjunto de
arquivos da disciplina. Embeddings são calculados localmente apenas para
textos novos ou alterados. Repetir com o índice compatível não escreve nem
recalcula embeddings. A conferência final ocorre antes do commit.

## API interna

A disciplina usa a rota existente, sem um endpoint separado:

```http
POST /internal/v1/chat
Content-Type: application/json
```

```json
{
  "pergunta": "Qual é a estrutura básica de uma história de usuário?",
  "disciplina": "projeto_de_ideacao_de_software",
  "assunto": "historias_de_usuario"
}
```

`assunto` é opcional. Ideação utiliza busca híbrida com reordenação própria:
até 50 candidatos da busca existente são ordenados por BM25 normalizado
(peso 0,7) e similaridade de cosseno (peso 0,3). Isso evita que slides gerais
ocultem termos específicos, como SCAMPER ou métricas de vaidade. A consulta
lexical reconhece UCD/Design Centrado no Usuário e PUV/Proposta Única de
Valor conforme as equivalências apresentadas nos slides; o embedding e a
pergunta enviada ao monitor preservam a pergunta original. O perfil de
Estrutura de Dados Avançada permanece vetorial.

O contexto pode conter menos de cinco trechos: candidatos abaixo de 65% da
relevância da melhor evidência são descartados, reduzindo complementos sem
relação direta com a pergunta. Páginas complementares com relevância próxima
continuam elegíveis. Esse corte também é experimental.

O monitor mantém Top-K 5 e aceita cosseno a partir de 0,25 ou cobertura
lexical ponderada a partir de 0,5 como entrada para a avaliação de contexto;
esses valores são experimentais e não comprovam suficiência por si só. Usa
citações `[F1]` etc. e até duas reformulações quando falta contexto. Perguntas
sem apoio no material retornam fallback. O contrato completo e os códigos
de erro estão em `API_CHAT_INTERNO.md`.

## Validação

```powershell
& '.\.venv\Scripts\python.exe' -B -m unittest discover -s test -p 'test_*.py' -v
& '.\.venv\Scripts\python.exe' -B -m scripts.validar_ideacao

# Envia perguntas e trechos ao OpenRouter configurado.
& '.\.venv\Scripts\python.exe' -B -m scripts.validar_ideacao --respostas

# Testa a rota FastAPI com banco e modelo reais, sem iniciar um servidor TCP.
& '.\.venv\Scripts\python.exe' -B -m scripts.validar_ideacao --respostas --http --casos historia_estrutura fora_disciplina
```

Os 23 casos têm páginas de referência declaradas antes da busca, cobrem as
cinco aulas, filtros de assunto e pergunta fora da disciplina. Os relatórios
registram os trechos recuperados, a conferência das fontes e, quando há
geração, as tentativas, as respostas e os trechos citados. Uma fonte válida
não comprova, sozinha, que a explicação está correta: a revisão semântica
precisa comparar cada resposta ao material citado.

As listas explicitamente enumeradas no material também têm verificações de
completude: seis etapas do UCD, sete ações do SCAMPER, nove blocos do Lean
Canvas, três níveis de fidelidade e nove estados de interface, entre outras.
Essas verificações identificam omissões, mas não substituem a revisão de
significado e de fidelidade das afirmações.

Relatórios: `saidas_testes/validacao_busca_ideacao.json`,
`saidas_testes/validacao_respostas_ideacao.json` e
`saidas_testes/validacao_respostas_ideacao_http_selecionados.json`.
`--casos` grava um arquivo separado e preserva o lote completo anterior.

## Resultado em 27/10/2026

- Cobertura: cinco aulas, 180 páginas, 217 chunks e seis revisões visuais.
- Índice PostgreSQL/pgvector: 217 registros, sem ausências, extras ou
  divergências de conteúdo/metadados. Repetir a indexação não insere,
  atualiza, remove ou recalcula embeddings.
- Testes locais do serviço: **66 aprovados**.
- Busca real com o perfil final: **23 de 23 casos aprovados**, incluindo
  filtros de assunto e pergunta fora do conteúdo.
- Respostas reais: **23 cenários aprovados na validação acumulada**, sendo
  22 perguntas acadêmicas e um fallback fora da disciplina. As respostas e
  suas fontes passaram por revisão semântica; cinco casos usam uma execução
  posterior com o contexto mais focado.
- Rota FastAPI com banco e modelo reais: **dois cenários aprovados**, ambos
  HTTP 200, usando TestClient e a instância real do Monitor. Essa conferência
  não representa uma integração com o Spring Boot.

O registro consolidado é `saidas_testes/validacao_final_ideacao.json`. Ele
identifica a execução usada em cada caso, conserva os hashes dos relatórios
de origem e registra as observações da revisão semântica. Não se apresenta a
validação acumulada como um único lote de 23 gerações. Os relatórios de
diagnóstico e as respostas anteriores permanecem preservados.

As listas do UCD e do SCAMPER foram conferidas completas. A comparação de
métricas recupera a página 27 mesmo com cosseno abaixo de 0,25, por sua
evidência lexical; a lista de estados preserva os nove itens em um único
trecho. JSON duplicado devolvido pelo provedor em uma tentativa foi recusado
pelo serviço, e a nova execução do caso passou com uma resposta válida.

Os resultados verificam a amostra declarada; não garantem todas as perguntas
possíveis. Os parâmetros de busca podem exigir nova calibração com novos
materiais ou uma amostra maior de perguntas.

A disciplina também possui integração com o catálogo Spring Boot e a interface
React pela migration V6 e pelo vínculo dos materiais. Consulte
`../docs/BACKEND_IDEACAO.md` para aplicar e validar essa integração.
