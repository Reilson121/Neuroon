# Estrutura de Dados — 2º período

Slug próprio: `estrutura_de_dados`. Não reutiliza assuntos, IDs ou materiais de
`estrutura_de_dados_avancada` (3º período).

## Fontes e limites

Nove unidades de aula em C, mais a transcrição parcial da UP1 de Aldo Moura:
quatro questões objetivas, sem gabarito oficial fornecido. As duas questões
abertas não estão no arquivo. A informação de que eram exercícios de lógica
no papel veio do aluno; não é uma transcrição dessas questões.

O catálogo abrange fundamentos de C; expressões, decisões, laços e escopo;
vetores e matrizes; registros; ponteiros; listas; filas; pilhas; introdução a
árvores e grafos. A referência à UP1 orienta formatos (seleção de conceitos,
tipos, sintaxe e análise de afirmações), sem limitar os assuntos das questões
inéditas à primeira unidade nem atribuir ao professor questões inventadas.

## Geração e correção

Na API pública, `tipoQuestao` aceita `MISTO`, `CONCEITUAL`, `ESTILO_PROFESSOR`,
`LOGICA`, `TESTE_MESA`; `nivelContexto` aceita `DIRETO`, `COTIDIANO`, `DETALHADO`.
Ambos são opcionais e preservam os clientes existentes. As preferências são
apresentadas apenas nesta disciplina. O modo dos materiais conserva as quatro
objetivas originais, separadas do modo de geração.

A geração é híbrida: modelos conceituais revisados e dados parametrizados,
simulação local de estados e narrativa contextual do provedor já configurado
no projeto. A IA não escolhe nem altera o gabarito. O modo direto dispensa a
chamada ao provedor. Contextos cotidianos e detalhados usam uma chamada em lote,
com validação de formato e restrições de dados. Falhas não são disfarçadas como
questões geradas com sucesso. Os PDFs são dados acadêmicos, nunca instruções
para executar ações ou alterar as regras da aplicação.

O enunciado orienta o trabalho no papel; a resolução só aparece após responder.
Nos exercícios de simulação, a correção inclui estados em tabela Markdown e
pseudocódigo de apoio. Código C não é executado a partir de texto do modelo:
o motor calcula os estados dos exemplos conhecidos. Não há comportamento C
indefinido, dependência de endereço real ou tamanho universal presumido de int.

Repetições são filtradas por identidade do exercício, sem contar como novidade
a simples troca da narrativa, ordem das alternativas ou parâmetros não usados.
Conceitos têm um conjunto finito de modelos; a seleção pode devolver menos
itens se o aluno já tiver visto todos. A revisão explícita permite refazê-los.

## Preparação e integração local

Na pasta `neuron-ai`, com o ambiente Python do projeto:

```powershell
./.venv/Scripts/python.exe -m scripts.preparar_ed_basica --origem 'PASTA DOS DEZ PDFS'
./.venv/Scripts/python.exe -m scripts.servicos_local migrar
./.venv/Scripts/python.exe -m scripts.integrar_materiais_ed_basica
./.venv/Scripts/python.exe -m unittest discover -s test -p test_ed_basica.py -v
```

A migration V10 adiciona somente esta disciplina. O índice compartilhado
preserva material, assunto, período, página e hash do arquivo. A prática de IA
com referência a todos os materiais usa os slides para cobrir os nove assuntos.
A referência apenas à prova limita corretamente a geração aos assuntos da
transcrição. Revogação e suspensão de materiais usam as regras existentes.
