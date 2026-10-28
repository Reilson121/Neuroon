# Estatística no NEURON

## Conteúdo integrado

Disciplina do terceiro período, organizada pelos 31 assuntos do mapa aprovado em app/rag/mapas/estatistica.py. O PDF possui 176 páginas: 166 de conteúdo e dez separadores excluídos. Foram processadas 63 páginas textuais e 103 visuais; quatro mesclagens internas aos assuntos resultaram em 162 páginas processadas e 193 chunks teóricos.

Os quatro arquivos recebidos estão preservados, com hashes e datas no inventário. rotacoes.py é código de AVL e permanece fora da ingestão. A proposta inicial está em ESTATISTICA_PROPOSTA.md; este documento descreve a implementação posterior à aprovação.

O preparo reutiliza AssuntoProcessor, DocumentProcessor, ChunkProcessor, index_sync, VectorStore, Retriever e MonitorVirtual. Os slides alimentam o Monitor; listas e provas ficam excluídas da recuperação teórica.

## Cadastro e avaliações

As migrations do Spring criam o núcleo relacional e cadastram período, Estatística, 31 assuntos e três materiais:

| Material | Tipo | Uso |
|---|---|---|
| estatistica_novo.pdf | SLIDE_AULA | Monitor Virtual |
| Exercissios 1 Unidade.docx | LISTA_EXERCICIOS | Prática autorizada |
| prova anterior de estátisitica.pdf | PROVA_ANTIGA | Prática autorizada |

Os chunks mantêm IDs relacionais de período, disciplina, assunto e material, além da proveniência no JSONB. O título descritivo dos slides é preservado; o título do cadastro é registrado separadamente. Páginas físicas, páginas mescladas, arquivo, hashes e metadados documentais originais continuam disponíveis.

Há nove questões distintas e 15 vínculos de origem: seis na lista e nove na prova. Cada questão é indexada inteira, sem separar alternativas ou subitens. A recuperação deduplica os enunciados compartilhados e apresenta somente origens atualmente autorizadas. O DOCX não fornece paginação estável: a referência usa título e número da questão, com página nula.

A prática cadastrada possui seis questões originais de múltipla escolha. As três discursivas permanecem como referências para geração. Dados pessoais, notas e identificação do estudante da prova digitalizada não foram incluídos nas transcrições.

## Revisões e gabaritos

- A autorização do professor para lista e prova foi declarada pelo usuário e consta de propostas/estatistica/.
- A autoria oficial do gabarito da lista permanece não confirmada. Não atribuir essas respostas ao professor como gabarito oficial.
- Resoluções de IA são identificadas; sem gabarito, aparece o aviso de que precisam ser conferidas.
- A questão original sobre covariância possui uma simplificação dependente da escala. A prática informa a ressalva, preservando o enunciado.
- Slides originais permanecem intactos. Observações de revisão por IA em estatistica_revisoes.json são separadas e não representam correção oficial.
- Quartis usam R7: índice zero h=(n−1)q e interpolação linear, explicitados nas questões. A convenção diferente da lista continua preservada.

Tabelas e gráficos foram conferidos contra as páginas originais. Trechos cortados não foram completados com números inventados. O corpus preserva a extração automática anterior nas páginas com correção de transcrição visual.

## Geração de questões

A geração é híbrida: o modelo já configurado no OpenRouter cria contextos narrativos; dados, condições matemáticas, alternativas, gabaritos e cálculos são montados e conferidos por código. São 20 famílias nos seis assuntos contemplados pelas avaliações: fundamentos de probabilidade, análise combinatória, probabilidade condicional, tendência central, dispersão/posição e correlação.

Há interpretação, cálculo, tabelas de frequências e dados para gráficos de barras e dispersão. Cada questão tem cinco alternativas distintas e uma resposta conferida. A correção entrega resultado, alternativa correta, conceito, fórmula, substituição, passos, explicação, erros comuns e dica.

Assuntos sem referências de avaliação retornam estado vazio, inclusive no modo IA. O modo cadastrado nunca chama o gerador para preencher ausência. Questões novas não são apresentadas como oficiais.

Sessões e fingerprints recentes ficam em memória. A exclusão de fingerprints reduz repetições durante a execução; reinícios apagam esse contexto. O modo de revisão permite revisitar questões cadastradas.

As conversas do Monitor têm histórico persistente no Spring, preservado e integrado por autorização adicional do usuário em 28/10/2026. Perguntas, respostas e referências pertencem ao usuário autenticado e podem ser reabertas após novo login. Essa persistência não altera o caráter temporário das sessões de prática.

## Integridade e permissões

O cadastro relacional governa disponibilidade. A prática exige disciplina e período ativos, possui_prova=true, lista ou prova ativa, autorização e disponibilidade. Spring revalida ao iniciar e corrigir; a consulta interna também restringe pelo cadastro.

O Monitor consulta fontes teóricas habilitadas. Disciplinas cadastradas não recuperam chunks sem vínculo com material. O legado de disciplinas ainda não migradas mantém compatibilidade com o protótipo.

O corpus completo é validado antes da ingestão. A sincronização é delimitada por disciplina, tipo e arquivo. Não remove questões ao atualizar slides, nem slides ao atualizar avaliações. Contagens e assinaturas das demais disciplinas são conferidas no relatório. Repetir a sincronização não cria registros ou recalcula embeddings quando o conteúdo é idêntico.

## Execução e evidências

Na pasta NEURON/neuron-ai:

    .\.venv\Scripts\python.exe -B -m scripts.servicos_local migrar
    .\.venv\Scripts\python.exe -B -m scripts.integrar_materiais_estatistica
    .\.venv\Scripts\python.exe -B -m scripts.monitor_estatistica --verificar-base
    $env:HF_HUB_OFFLINE='1'
    $env:TRANSFORMERS_OFFLINE='1'
    .\.venv\Scripts\python.exe -B -m scripts.validar_estatistica

O preparador mantém plano, amostra, processamento e conferência. Não é necessário reenviar as 103 páginas já extraídas para repetir a ingestão. O checkpoint recusa PDF, mapa ou modelo divergentes.

Evidências em saidas_testes: estatistica_integracao_materiais.json, estatistica_validacao_busca.json, estatistica_validacao_respostas.json e estatistica_validacao_backend.json. Os relatórios distinguem verificações automáticas de revisão semântica. O relatório HTTP registra a execução efetivamente aprovada, sem segredos ou contas reais.

Contratos e inicialização estão em ../docs/BACKEND_ESTATISTICA.md. A integração com o frontend existente foi retomada por solicitação do usuário e validada com dados reais; veja ../docs/FRONTEND_ESTATISTICA.md.
