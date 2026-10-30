# Cálculo para Computação II

Disciplina do 3º período, slug `calculo_para_computacao_2`.

O escopo foi informado pelo aluno: integrais simples indefinidas e definidas, duplas e triplas por cálculo direto. A primeira unidade contém somente uma variável. A segunda unidade organiza as múltiplas como proposta didática, pois não foi fornecida uma ementa oficial com essa distribuição.

## Materiais e chat

- Guia de Integrais - NEURON: sete páginas, com explicações, exemplos resolvidos, questões e respostas.
- Tabela de Integrais - apoio NEURON: duas páginas de consulta. Substituição e partes aparecem como consulta adicional, sem alegação de cobrança confirmada.
- Simulados abertos de Integrais - NEURON: duas provas autorais, uma por unidade, e dois gabaritos comentados. Cada simulado propõe 8 pontos e 180 minutos. São inspirados nos comandos diretos, subitens e consulta a fórmulas da prova transcrita de Cálculo I, não questões oficiais de Cálculo II.
- PDF de funções de várias variáveis recebido: preservado integralmente, identificado como complemento criado com IA e fornecido pelo aluno. Domínio, avaliação e variáveis fixas são base opcional. Gradiente, otimização, Lagrange e mudanças de coordenadas não entram na cobrança nem nos simulados padrão.

Os apoios autorais não são atribuídos ao professor. A prova de Cálculo I e os livros de derivadas permanecem em sua disciplina e servem apenas como referência de formato ou pré-requisito, sem serem registrados como aulas de integrais. O corpus registra autoria, caráter complementar, unidade, arquivo, página e SHA-256; nenhum registro declara prova oficial. O chat prioriza as fontes curriculares e só recupera o complemento amplo para pedidos pertinentes.

## Prática

O motor `integral_engine.py` calcula primitivas, integrais diretas e definidas (polinomiais, radicais, racionais, trigonométricas e exponenciais), duplas em retângulos ou com limites variáveis e triplas em caixas ou com limites variáveis. Os limites são fornecidos, em cartesianas. A prática complementar de valor de função fica disponível no assunto opcional.

Integrais racionais do banco usam x>0; o guia e a tabela explicam ln|x| em cada intervalo sem zero. Radicais respeitam o domínio real. Os distratores de primitivas alteram a derivada, pois alternativas que diferissem somente por constante seriam todas corretas. A conferência reconstrói as etapas e valida primitivas por derivação e definidas por integração simbólica.

A interface permite prática, simulado por assuntos, por unidade, final e segunda chamada. Os simulados padrão incluem apenas os sete assuntos curriculares; a final e a segunda chamada cobrem ambos os blocos. Durante a tentativa, o gabarito e as resoluções permanecem ocultos até a entrega, seguindo o comportamento de Cálculo I. A plataforma usa cinco alternativas de conferência, com essa adaptação explícita; os PDFs mantêm questões abertas.

O campo legado `possui_prova=true` habilita a prática e os simulados na plataforma. Não descreve a existência de avaliação oficial. Os quatro PDFs são `RESUMO`, com fonte do Monitor ativa, sem autorizações fictícias de prova do professor.

## Preparação e ativação

1. `scripts/preparar_calculo2.py --pdfs` gera os três PDFs autorais; requer ReportLab e a fonte Cambria do Windows. Os arquivos finais já estão incluídos no diretório de materiais.
2. `scripts/preparar_calculo2.py --corpus` preserva o complemento original e cria o corpus de 85 páginas físicas e 216 trechos. Requer PyMuPDF.
3. Aplicar a migration `V13__catalogo_calculo_2.sql`.
4. Executar `python -B -m scripts.integrar_materiais_calculo2`, com o mesmo banco e modelo de embeddings das outras disciplinas.
5. Reiniciar os serviços com o código atualizado para usar os novos filtros e o motor. Em uma instalação hospedada, reconstruir as imagens e disponibilizar os PDFs/corpus no volume de materiais antes de indexar.

Os testes Python cobrem cálculos com valores conhecidos, derivação de primitivas, unicidade das respostas, adulteração, origem, separação de unidades, buscas e cobertura dos simulados sem vazamento de gabarito. Os testes React cobrem tabela, filtros e exclusão do complemento nas provas das unidades, final e segunda chamada.
