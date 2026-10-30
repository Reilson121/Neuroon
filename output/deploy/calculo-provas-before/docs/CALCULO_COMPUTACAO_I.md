# Cálculo para Computação I

Disciplina do **2º período**, slug `calculo_para_computacao_1`.

## Organização

| Unidade | Assuntos | Tópicos de prática |
| --- | --- | --- |
| 1 | Funções compostas | Composição com funções polinomiais, racionais e radicais |
| 1 | Funções inversas | Inversa de afim e exponencial |
| 1 | Simplificação algébrica | Fatoração e restrições do domínio |
| 1 | Limites | Substituição, fatoração 0/0, racionalização, infinito e confronto |
| 1 | Limites laterais e continuidade | Função por partes, limites dos dois lados e valor no ponto |
| 2 | Definição de derivada | Quociente incremental |
| 2 | Regras de derivação | Potência, soma, produto, quociente, cadeia; polinômios, radicais, racionais, trigonométricas, exponenciais, logaritmos e hiperbólicas |
| 2 | Derivação implícita | Relação entre x e y |
| 2 | Aplicações | Tangente, taxa instantânea, crescimento/decaimento, taxas relacionadas, linearização e diferencial |

O catálogo também indica os tópicos teóricos dos livros, como definição precisa de limite, injetividade e derivabilidade. O treino parametrizado cobre as famílias enumeradas acima; não pretende substituir todos os exercícios dos livros.

## Fontes e proveniência

Cinco PDFs recebidos: três trechos de livros, a tabela do Prof. Douglas Maioli e a prova transcrita da **1ª unidade**. São 202 páginas físicas. O corpus preserva arquivo, página, assunto, unidade e SHA-256; uma página pode pertencer a mais de um assunto com identificadores distintos. A primeira página da tabela tem transcrição das fórmulas conferida visualmente, pois a extração automática dos expoentes é defeituosa. As páginas originais ficam disponíveis no leitor. A extração textual dos livros pode perder fórmulas ou informações de gráficos; o Monitor deve informar insuficiência quando não houver suporte, sem reconstruir fórmulas ausentes.

Não há prova da segunda unidade nem gabarito oficial. Na prova transcrita, falta o item 2b e não há valor de f(1) em 8A. Esses dados não são preenchidos. A prova aberta continua acessível como PDF e fonte do Monitor; não é apresentada como uma prova objetiva original. Para praticar na interface existente, os exercícios inéditos usam comandos diretos de cálculo e cinco alternativas de conferência, com essa adaptação informada ao estudante.

## Integração

- Migration `V11__catalogo_calculo.sql`: período, disciplina, nove assuntos e cinco materiais. Livros são `TRECHO_LIVRO`, tabela é `RESUMO`; não são disfarçados de slides.
- Preparação: `python -B -m scripts.preparar_calculo --origem PASTA_DOS_PDFS` em `neuron-ai`. Copia sem alterar os originais, gera `corpus.json` e o catálogo de tópicos compartilhado com a interface.
- Aplicação local do catálogo: `python -B -m scripts.servicos_local migrar`.
- Indexação: `python -B -m scripts.integrar_materiais_calculo`. Exige a migration, confere hashes e usa o índice compartilhado, com materiais e assuntos ativos.
- O Monitor usa o provedor de IA já configurado, recuperação híbrida e referências verificadas. O prompt exige passos e sugere a tabela nas derivadas.
- Ao citar o número de uma questão da prova, a busca prioriza o trecho correspondente, respeitando as permissões do material. Pedidos sobre uma regra de derivação usam sua seção e a tabela, evitando exercícios de outras seções; exemplos adicionais dependem do pedido do aluno.
- A prática usa um motor parametrizado próprio e SymPy 1.14.0. Não chama o narrador de Estatística nem adiciona histórias aos enunciados. O cálculo, a solução e o gabarito são reconstruídos e conferidos antes da exibição e na correção.
- Filtros transmitidos React → Spring → Python: `unidadeCalculo` (0/todas, 1 ou 2), `topicoCalculo` e `tipoFuncao`. Seleção incompatível retorna ausência de questões; não muda silenciosamente a regra, o tipo ou a unidade.
- Alterar qualquer filtro invalida a sessão visível e cancela respostas antigas. O aluno recebe solução, regra, substituição, operações, restrições, erro comum e dica somente depois da resposta. O link da tabela usa a rota de materiais autenticada existente.
- Os PDFs e o corpus ficam no volume de materiais já usado pela implantação. A imagem da IA declara SymPy e inclui o novo indexador. Publicar a atualização requer reconstruir as imagens, aplicar a migration e indexar o corpus na instalação de destino.

## Verificação

Testes Python cobrem todas as combinações de tópico e função, conferência numérica independente, separação de unidades, hashes, unicidade, filtros, ausência de vazamento do gabarito e recusa de soluções adulteradas. Testes Java cobrem repasse dos filtros, livros/tabela e isolamento do período. Testes React cobrem opções compatíveis, limpeza de filtros, invalidação de prática e abertura da tabela.
