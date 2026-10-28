# Monitor Virtual - Design de Artefatos Digitais

Corpus do período 03: oito aulas e o material complementar da Matriz CSD.
Os nove PDFs somam 310 páginas. O consolidado contém 363 chunks, com cobertura
de todas as páginas e referências ao arquivo, à aula, ao assunto e à página.

## Preparação e revisão

- Os nove JSONs individuais de ingestão permanecem intactos.
- Quarenta e uma páginas receberam revisões locais, conferidas nas imagens dos PDFs.
  Foram recuperadas definições em imagens, exemplos visuais, etapas do Design
  Thinking e relações do mapa de empatia. A Matriz CSD foi reestruturada por
  coluna, retirando textos de animações que não estavam visíveis no slide.
  A lista de fatores do consumidor recebeu o título literal da página anterior
  como contexto, com as duas páginas preservadas nas referências.
- Foi removido um caractere NUL da página 19 da Aula 05, incompatível com TEXT
  no PostgreSQL. Os demais símbolos do conteúdo foram preservados.
- As revisões estão em `app/rag/mapas/design_revisoes.json`, com justificativa,
  hash do PDF e hash do conteúdo anterior de cada página.
- O corpus consolidado é
  `saidas_testes/design_de_artefatos_digitais_completa.json`. Seu manifesto
  registra os hashes dos PDFs, dos JSONs de origem e das revisões. A preparação
  rejeita páginas ausentes, repetidas, vazias ou com identidade inconsistente.
- Recriar o corpus não chama modelos externos nem reprocessa a visão.
  O monitor e o indexador rejeitam um consolidado diferente das fontes atuais.

## Executar

Na pasta `C:\Projeto Extensionista 2\NEURON\neuron-ai`:

```powershell
& '.\.venv\Scripts\python.exe' -B -m scripts.preparar_design
& '.\.venv\Scripts\python.exe' -B -m scripts.indexar_design
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_design --verificar-base
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_design --somente-busca 'O que é harmonia triádica?'
& '.\.venv\Scripts\python.exe' -B -m scripts.monitor_design 'Quais são as cinco etapas do Design Thinking?'
```

Somente o último comando gera resposta pelo OpenRouter. A indexação calcula
embeddings localmente, insere apenas IDs ausentes e atualiza apenas os trechos
divergentes. Preserva metadados extras e campos relacionais dos registros
existentes. A aplicação e a conferência ocorrem em uma transação, com rollback
em caso de erro e detecção de alterações concorrentes. IDs obsoletos só são
removidos na disciplina e no conjunto de arquivos do corpus. Repetir com o
índice compatível não escreve nem recalcula embeddings.

O monitor usa o RAG compartilhado com um perfil de recuperação específico para
Design: busca semântica exata no conjunto da disciplina, BM25 contextualizado
pelo assunto, fusão de rankings e redução de slides repetidos. O perfil vale
tanto no comando de Design quanto na rota interna de chat. O fluxo vetorial
de ED Avançada permanece com seu perfil anterior.

O contexto tem até cinco trechos. Um trecho pode chegar ao modelo por
similaridade de cosseno de pelo menos 0,25 ou cobertura lexical ponderada de
pelo menos 0,5; esses valores são experimentais. A cobertura lexical permite
recuperar definições com termos específicos mesmo quando o embedding não
reconhece bem esses termos. O cosseno original é preservado nos metadados.
O modelo precisa verificar se o conteúdo realmente sustenta a resposta.

O retorno usa citações `[F1]` etc. e até duas reformulações quando o contexto
é insuficiente. JSON válido envolto integralmente em uma cerca Markdown é
aceito; prosa fora do objeto, JSON inválido e geração incompleta continuam
sendo recusados. `--assunto` aceita os nove assuntos do corpus e restringe a busca.
Os mesmos parâmetros são aceitos pela rota interna de chat já existente:

```json
{
  "pergunta": "O que é harmonia triádica?",
  "disciplina": "design_de_artefatos_digitais",
  "assunto": "design_de_interface_diagramacao"
}
```

## Validação reproduzível

```powershell
& '.\.venv\Scripts\python.exe' -B -m scripts.validar_design
& '.\.venv\Scripts\python.exe' -B -m scripts.validar_design --respostas
```

O primeiro comando faz apenas busca. O segundo envia perguntas e trechos
acadêmicos recuperados ao modelo já configurado no OpenRouter e pode consumir
créditos. Os casos cobrem os nove materiais, conceitos específicos, definições
visuais reparadas, filtro de assunto e pergunta fora da disciplina. As páginas
esperadas são declaradas antes da execução. O relatório confere cada fonte
contra o corpus e conserva as tentativas de geração para revisão semântica.
Uma referência existente, isoladamente, não prova a correção de uma afirmação.
No teste de busca, a pergunta fora da disciplina é apenas registrada: a recusa
semântica é verificada no lote de respostas, em vez de tratar o limiar de
similaridade como um classificador de assuntos.

Relatórios: `saidas_testes/validacao_busca_design.json` e
`saidas_testes/validacao_respostas_design.json`. Ao usar `--casos`, o comando
grava um relatório separado com sufixo `_selecionados`, preservando o lote
completo anterior.

## Estado da validação

- Consolidação, cobertura e repetibilidade: verificadas.
- Banco conferido: 363 chunks, zero ausências, extras ou divergências de texto
  e metadados; pgvector 0.8.5, embeddings de 384 dimensões.
- Repetição da indexação com a base compatível: zero inserções, atualizações,
  remoções e embeddings recalculados.
- Suíte local: 61 testes aprovados, incluindo corpus, sincronização, busca,
  monitor e contrato da rota interna de chat.
- Busca real: as 18 perguntas acadêmicas recuperaram as páginas esperadas entre
  os cinco primeiros resultados. Fontes e filtro de assunto conferidos.
- Respostas reais via OpenRouter: 18 perguntas acadêmicas respondidas com
  fontes do corpus e uma pergunta fora da disciplina recusada sem fontes.
  As 19 respostas finais foram conferidas pelo agente contra os trechos
  citados e os objetivos dos casos; não houve revisão humana externa.
- Uma saída malformada de JSON no teste fora da disciplina foi recusada pelo
  sistema. Esse caso foi reexecutado isoladamente, confirmou a recusa por falta
  de conteúdo e foi incorporado ao relatório final, preservando a falha anterior
  em `historico_validacoes`. O formato inválido não foi aceito nem corrigido
  silenciosamente.

O relatório `saidas_testes/indexacao_design.json` registra a sincronização e a
auditoria. As execuções vetoriais iniciais, com falhas, foram preservadas em
`validacao_busca_design_vetorial_inicial.json` e
`validacao_respostas_design_vetorial_inicial.json` para diagnóstico. A validação
final está nos relatórios sem esse sufixo, com o perfil híbrido e o corpus atual.

A integração com o catálogo do backend e a interface está descrita em
`../docs/BACKEND_DESIGN.md`: migration V5, nove assuntos e nove PDFs,
vínculos relacionais dos trechos, Monitor com filtro de assunto, fontes e
histórico. A prática permanece indisponível sem avaliações autorizadas.
Os resultados acima se referem à validação do RAG e não substituem a
validação da integração pela API pública.
