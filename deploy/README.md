# NEURON publicado na VPS

Endereço: https://neuron-45-159-173-74.sslip.io/

Implantação em 29/10/2026 na VPS Serverspace 45.159.173.74, São Paulo, 4 vCPUs, 8 GB RAM e 60 GB SSD. Ubuntu 20.04 mantido por escolha do usuário. A versão do sistema foi conferida antes da instalação; seu suporte padrão já terminou. O piloto usa um subdomínio sslip.io que depende da continuidade desse serviço e do mesmo IP.

## Serviços e dados

A pasta privada no servidor é `/opt/neuron`. Docker Compose executa PostgreSQL 18 com pgvector, backend Java 17, IA Python 3.13 em CPU e Caddy para interface/HTTPS. Somente as portas da interface 80/443 são publicadas; banco e serviços internos ficam na rede Docker.

A migração preservou 4 contas originais, históricos, 32 materiais cadastrados e 1308 chunks do índice. Foram transferidos 43 arquivos da pasta de materiais. O dump inicial e o pacote de transferência estão em `deploy/backups/` no computador, ignorados pelo Git. Os materiais são montados somente para leitura. O cache do modelo e os dados do PostgreSQL usam volumes persistentes.

`deploy/.env` no servidor contém senha exclusiva de banco, token interno e configuração OpenRouter. Não publicar nem imprimir esse arquivo. Os segredos não estão nas imagens. `deploy/access/` guarda a chave SSH e arquivos privados de transferência no computador; manter essa pasta privada e fora do Git.

O acesso usa conta e senha. As contas já existentes foram migradas; novos estudantes podem se cadastrar. Visitante está desativado no backend e oculto na interface de produção. A interface local mantém seu comportamento padrão. Não definir variáveis vazias de bootstrap: elas acionam indevidamente a criação do administrador. Esta instalação utiliza os administradores migrados.

## Verificações realizadas

- HTTPS válido, interface aberta em navegador externo ao servidor e login de estudante.
- PDF servido e conferido pelo cabeçalho do arquivo (16.266.761 bytes).
- 30 contas e sessões independentes em paralelo: 120 consultas autenticadas de catálogo, materiais e assuntos, sem falhas. O gerador do teste rodou na VPS acessando o endereço HTTPS público; não mede a conexão residencial dos alunos nem substitui teste prolongado.
- Monitor Virtual: resposta real em 2,69 segundos, três fontes, selecionando Estatística > Medidas de tendência central.
- Prática: criação de questão cadastrada e correção com resolução.
- Backend e IA reiniciados: ambos saudáveis; cache do modelo e dados preservados.
- As 31 contas sintéticas dos testes foram removidas; restam as 4 contas originais.
- Backup após publicação copiado para `deploy/backups/neuron-after-deploy.dump` e validado com `pg_restore --list`.

A capacidade de 30 perguntas simultâneas à IA ainda não foi medida. O executor atual processa inicialmente duas perguntas e usa fila; demanda concentrada pode aumentar espera ou atingir o tempo limite. O teste de navegação não garante 30 gerações de IA simultâneas.

Perguntas sem assunto podem receber recusa por falta de contexto mesmo quando há conteúdo no PDF: a busca vetorial original pode recuperar trechos pouco relevantes. Selecionar o assunto melhora o resultado. Não foi alterado o mecanismo de recuperação durante a hospedagem.

## Operação

### Atualização: avaliações públicas — 30/10/2026

A consulta de avaliações fica disponível sem login em `/#avaliacoes`, pelo link
“Ver avaliações dos alunos” na entrada e pela opção “Avaliações” do menu.
Exibe nome, nota, comentário, data no horário de Fortaleza, média geral e
quantidades, com dez respostas por página. O formulário informa que a avaliação
é pública. O envio continua restrito à própria conta de estudante autenticada.

Publicado somente backend e interface, sem migration. A conferência pelo HTTPS
confirmou duas avaliações, média 4,5, ausência de email/senha na resposta pública,
proteção das rotas privadas, arquivos publicados e serviços saudáveis.
Backup no servidor: `/opt/neuron/deploy/backups/avaliacoes-20261030T175232Z/`.
Relatório: `/opt/neuron/verificacao-avaliacoes-publicadas.json`.
Preparação, atualização e conferência em `output/deploy/*avaliacoes*`.

### Atualização: Cálculo para Computação II — 29/10/2026

Publicada a migration V13 no 3º período, com oito assuntos, quatro PDFs e 216
trechos no índice. A primeira unidade contém somente integrais de uma variável;
a segunda reúne duplas e triplas por cálculo direto em cartesianas. O complemento
de funções de várias variáveis é opcional e fica fora dos simulados padrão.

IA, backend e interface foram reconstruídos. A aceitação pelo HTTPS público
confirmou os quatro PDFs por hash, geração e correção nas combinações de tópicos
e funções, consulta à tabela, simulados por conteúdos, por unidade, final e
segunda chamada. Três respostas reais do Monitor foram conferidas com fontes;
a prática de Cálculo I permanece funcionando. Contas permanentes e históricos
foram preservados, e a conta sintética de validação foi removida.

Relatório: `output/verificacao-calculo2-publicado.json` neste computador e
`/opt/neuron/verificacao-calculo2-publicado.json` na VPS. Backup anterior à
primeira tentativa em `/opt/neuron/deploy/backups/calculo2-20261030T022808Z/`;
backup da ativação final em `/opt/neuron/deploy/backups/calculo2-20261030T023621Z/`.
As duas tentativas anteriores restauraram automaticamente as imagens anteriores:
uma referência de outra atualização foi removida do pacote e o diretório dos
novos materiais recebeu permissão de leitura para os serviços. A ativação final
e a indexação terminaram com sucesso. As contas e os históricos não foram restaurados
por cima do uso real.

### Atualização: Estrutura de Dados do 2º período — 29/10/2026

Publicada a migration V10, com nove assuntos, dez PDFs e 180 novos trechos.
O índice passou de 1308 para 1488 trechos; os materiais cadastrados, de 32 para 42.
As seis contas e as catorze conversas existentes na VPS foram preservadas.
Estrutura de Dados Avançada permanece no terceiro período.

Backend, IA e interface foram reconstruídos e passaram nas verificações de saúde.
A aceitação pelo HTTPS público confirmou os novos controles, os dez PDFs,
prática e correção nos nove assuntos, as quatro objetivas da prova parcial e
contextualização real pelo provedor (1,36 segundo na amostra). A conta sintética
foi removida ao encerrar a verificação. O relatório está em
`output/verificacao-estrutura-de-dados-publicada.json` neste computador e
`/opt/neuron/verificacao-ed-basica-publicada.json` na VPS.

Backup prévio: `/opt/neuron/deploy/backups/ed-basica-20261029T173130Z/`,
contendo banco, fontes anteriores e contagens de referência. As imagens anteriores
estão marcadas com a versão `before-ed-20261029T173130Z`. O backup permanece na
VPS; a cópia adicional para este computador foi bloqueada pela revisão automática
por incluir dados privados de contas e históricos, sem autorização específica.
O banco online recebeu somente a migration e o índice da nova disciplina.

O registro SSH previamente utilizado foi preservado em
`deploy/access/known_hosts`, junto da chave privada já existente; manter a
verificação estrita de identidade nas próximas atualizações.

### Atualização: Cálculo para Computação I — 29/10/2026

Publicada a migration V11 no **2º período**, com nove assuntos, cinco PDFs e
678 novos trechos. O catálogo passou a 47 materiais e o índice a 2166 trechos.
Funções e limites ficam na primeira unidade; derivadas, na segunda. A prova
recebida continua identificada como sendo somente da primeira unidade.

Backend, IA e interface foram reconstruídos e estão saudáveis. A aceitação pelo
HTTPS público conferiu os cinco PDFs por hash, geração e correção nos 28 tópicos,
filtros por unidade/regra/função, acesso à tabela de derivadas e três respostas
reais do Monitor com fontes. A conta e as conversas sintéticas foram removidas.
O relatório está em `output/verificacao-calculo-publicado.json` neste computador
e `/opt/neuron/verificacao-calculo-publicado.json` na VPS.

As contas permanentes e seus históricos foram preservados. O banco contém sete
contas, doze conversas e sessenta mensagens após a conferência.
A comparação com o backup identificou a atuação da rotina preexistente
`VisitanteCleanup`: um visitante com mais de 24 horas expirou, removendo suas
três conversas e oito mensagens temporárias. O relatório mantém essa distinção
explícita; o backup anterior permanece no servidor.

Backup prévio: `/opt/neuron/deploy/backups/calculo-20261029T195616Z/`, com banco,
fontes e referência anterior. Imagens anteriores:
`neuron-{backend,ai,web}:before-calculo-20261029T195616Z`.

### Atualização: prática de ED Avançada e Design — 29/10/2026

Publicada a migration V12, habilitando a prática autoral das duas disciplinas do
terceiro período. Estrutura de Dados Avançada oferece conceitos e testes de mesa
diretos ou contextualizados em 13 assuntos. Design tem 27 questões em nove assuntos
e prova simulada com seleção de conteúdos, revisão das escolhas e correção ao finalizar.

Backend, IA e interface foram reconstruídos; os serviços estão saudáveis. A aceitação
pelo HTTPS público confirmou catálogo, filtros, fontes, correções, seleção múltipla
e recusa de assuntos inválidos. A conferência interna gerou e corrigiu três questões
por assunto: 39 em ED Avançada e 27 em Design. A conta temporária foi removida;
contas permanentes, conversas, mensagens, materiais e índice existentes foram preservados.

Relatório: `output/verificacao-pratica-avancada-design-publicada.json` neste computador
e `/opt/neuron/verificacao-pratica-avancada-design-publicada.json` na VPS.
Backup prévio mantido no servidor:
`/opt/neuron/deploy/backups/pratica-avancada-design-20261030T012850Z/`.
As imagens anteriores têm a marca `before-pratica-20261030T012850Z`.

### Atualização: geração e provas de Cálculo — 29/10/2026

Publicada a correção da leitura de páginas compartilhadas por vários assuntos:
as referências de fatoração e funções inversas são preservadas. O motor de
Cálculo amplia as variações e a interface oferece provas por assuntos escolhidos,
primeira unidade, segunda unidade, final e segunda chamada. As duas últimas
reúnem os nove assuntos das duas unidades; todas exigem ao menos uma questão
por assunto e apresentam a correção ao finalizar.

Os três serviços foram reconstruídos, com backup prévio em
`/opt/neuron/deploy/backups/calculo-provas-20261030T015519Z/`.
As imagens anteriores têm a marca `before-calculo-provas-20261030T015519Z`.
A atualização envia somente dez arquivos e confere os hashes anteriores para
preservar alterações concorrentes. Não exige migration nem reindexação.
A formatação matemática do Monitor permanece na versão já publicada.

Procedimentos locais: `output/deploy/prepare-calculo-provas.py`,
`output/deploy/update-calculo-provas.sh` e `output/deploy/verify-calculo-provas.py`.
O relatório da aceitação fica em `/opt/neuron/verificacao-calculo-provas-publicado.json`
e em `output/verificacao-calculo-provas-publicado.json` neste computador.

A aceitação confirmou as cinco modalidades pelo HTTPS, a correção das dez
questões da final, 30 fatorações consecutivas distintas e a continuidade do
simulado de Design. No índice publicado, foram conferidas 430 questões nas
43 combinações dos 28 tópicos e outras 210 fatorações sem repetição.
Contas permanentes, históricos, catálogo, índice e formatação do Monitor foram
preservados; a conta temporária usada na conferência foi removida.

### Comandos de operação

Executar na pasta `/opt/neuron` do servidor:

```sh
docker compose --env-file deploy/.env -f deploy/compose.yaml ps -a
docker compose --env-file deploy/.env -f deploy/compose.yaml logs --tail 50 backend ai web
docker compose --env-file deploy/.env -f deploy/compose.yaml up -d
```

Para atualizar um serviço, enviar somente as fontes necessárias, construir sua imagem e recriar o serviço. Compilar um de cada vez. Não executar `docker compose down -v`, pois isso remove os volumes de dados. `index-schema` encerrado com código 0 é esperado.

O script `bootstrap-host.sh` instalou Docker e plugins das distribuições oficiais. `prepare-transfer.py` prepara dump, pacote autorizado e ambiente privado; `restore-initial.sh` recusa restauração em banco já preenchido. Não restaurar por cima de uso real. As dependências Python principais e o torch CPU estão fixados nas versões utilizadas na implantação.

## Custos e continuidade

O painel apresentado pelo usuário indicava R$ 0,198 por hora, aproximadamente R$ 4,75 por dia. R$ 25 equivalem a cerca de 126 horas no total, antes de outros serviços e de qualquer alteração de tarifa. Conferir saldo e consumo no painel; não há desligamento automático preparado. A cobrança pode continuar com recursos alocados mesmo sem visitantes e com a máquina parada. Fazer backup atualizado antes de excluir recursos para encerrar o piloto e conferir o encerramento da cobrança no painel.

OpenRouter tem cobrança e saldo próprios. Definir limite de gasto na conta antes de ampliar o público. Manter backups atualizados do banco fora da VPS; os volumes não substituem backups. O backup inicial no computador não inclui alterações posteriores feitas no site.
