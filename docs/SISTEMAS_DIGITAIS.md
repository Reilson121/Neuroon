# Sistemas Digitais

O catálogo contém 12 assuntos e 12 PDFs únicos do **2º período**. As duas cópias idênticas dos Downloads não são importadas. A disciplina possui prova, mas a prova e a lista ainda não foram fornecidas. Nenhum material desses tipos é inventado ou cadastrado.

A migration V9 corrige a classificação original da V7, movendo somente Sistemas Digitais para o segundo período e atualizando o período dos 353 trechos no índice. IDs, textos, embeddings, assuntos, materiais e conversas são preservados. As demais disciplinas continuam no terceiro período. A interface busca o catálogo pela API e acompanha essa mudança sem IDs fixos.

Os PDFs e o corpus bruto continuam no endereço físico original `materiais_academicos/periodo_03/sistemas_digitais` para preservar as referências existentes. Esse endereço de armazenamento não define o período curricular. O preparo para indexação exige o segundo período e normaliza os metadados para `02`, inclusive em futuras reindexações. O script de preparação exporta uma proposta SQL em `saidas_testes` e não sobrescreve migrations aplicadas.

## Monitor Virtual

O corpus tem 189 páginas com texto e 353 trechos. Vinte páginas de contracapa, aviso editorial e folhas brancas foram conferidas visualmente e excluídas da busca. Os PDFs originais são preservados. Cada trecho mantém arquivo, página física, assunto e SHA-256 do PDF. A busca híbrida e o Monitor existentes usam os filtros relacionais da disciplina e do assunto.

A extração é textual: diagramas, imagens e fórmulas com elementos exclusivamente gráficos não foram transcritos integralmente. O Monitor deve usar os trechos disponíveis e informar quando não houver evidência suficiente. Isso não equivale à revisão visual de todos os circuitos dos livros.

## Prática

Há 32 questões conceituais autorais de IA, com situações de aplicação, e sete famílias de exercícios lógicos e numéricos: portas, absorção, contagem, bits de contadores, codificação de estados, registradores e capacidade de memória. A absorção usa um problema fixo; as outras famílias variam os dados. A codificação de estados é reutilizada em três assuntos. As questões seguem os temas dos PDFs, sem copiar questões das avaliações que ainda não existem no projeto.

Cada questão tem cinco alternativas, resolução em etapas, explicação, erro comum, dica e fonte teórica por página. A fonte fundamenta o conceito; o cenário e sua resolução são autorais de IA. As operações numéricas e tabelas lógicas são calculadas localmente. As questões conceituais usam modelos revisados, sem depender de uma nova chamada ao provedor a cada prática.

A resposta correta e a resolução ficam no servidor até a tentativa. A conferência rejeita alterações no gabarito ou nos passos. Os identificadores de questão não mudam apenas por embaralhar as alternativas. Algumas seleções têm menos questões novas que o total pedido; a interface informa a limitação e permite revisar vistas.

A geração a partir da teoria se aplica apenas a Sistemas Digitais, no modo `GERADAS_IA` e referência `MISTO`. Não altera as exigências para questões de listas e provas: autorização, disponibilidade, usuário e disciplina continuam sendo conferidos. A permissão de fonte teórica é conferida novamente na correção. O modo cadastrado e os filtros de lista ou prova não tratam teoria como avaliação oficial.

## Preparação e integração

Na pasta `neuron-ai`, com o ambiente Python do projeto:

```powershell
python -m scripts.preparar_sistemas_digitais --origem 'C:\Users\Pichau\Downloads\Sistemas Digitais'
python -m scripts.servicos_local migrar
python -m scripts.integrar_materiais_sistemas_digitais
```

A migration V7 adiciona o catálogo; a V9 corrige o período sem modificar outras disciplinas. A integração usa o sincronizador existente com escopo por PDF. Reinicie os serviços locais após atualizar o código.

## Validação realizada

Em 29/10/2026, a V9 foi aplicada ao banco local. A conferência HTTP em
`scripts.validar_backend_sistemas_digitais` confirmou a disciplina somente no
segundo período, 12 assuntos, abertura autenticada dos 12 PDFs, os 353 trechos
com período `02` e uma sessão real de prática atravessando Spring e FastAPI.
A conta temporária foi removida. O relatório está em
`output/verificacao-sistemas-digitais.json`, na raiz de NEURON.
Sete testes Python e três testes da interface passaram, incluindo troca do
terceiro para o segundo período, filtro de assuntos, link do PDF e envio dos
IDs corretos à prática. A validação local gerou e corrigiu 105 questões.
Nenhuma chamada ao provedor pago foi feita; uma resposta nova do Monitor
com geração de linguagem não foi testada nesta conferência.

- Catálogo V7 aplicado e 12 PDFs indexados, com 353 trechos vinculados aos materiais e assuntos corretos.
- Busca do Monitor conferida separadamente nos 12 assuntos.
- Amostra de 105 questões gerada e corrigida usando as fontes reais do banco, sem expor gabaritos antes da tentativa.
- 21 testes direcionados de Python e 56 testes do servidor aprovados.
- 22 testes da interface aprovados nos oito arquivos; a execução foi dividida por arquivo após limites de tempo do ambiente.
- Compilação da interface para produção concluída.

Os relatórios estão em `neuron-ai/saidas_testes/sistemas_digitais_integracao.json` e `sistemas_digitais_validacao.json`. A amostra com enunciados e resoluções está em `sistemas_digitais_amostra_resolvida.json`. A consulta real ao provedor de linguagem não fez parte desta validação: foram conferidas a recuperação das fontes e a prática, além dos testes automatizados existentes do Monitor.

Não há PDFs próprios de Sistema de numeração, Codificadores e decodificadores, Multiplexadores e demultiplexadores e Memória RAM e cache. A menção de RAM no material geral de memórias não substitui o módulo específico ausente. O módulo “Projetos…” da captura ainda tem o título incompleto; o PDF disponível foi cadastrado com seu título real, Projetos de circuitos sequenciais.
