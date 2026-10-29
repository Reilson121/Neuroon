# Publicar o NEURON em uma VPS

Preparação inicial para Linux com Docker Compose. **Ainda não é uma implantação validada:** os builds dos containers, a restauração dos dados e o teste externo precisam ser concluídos antes de divulgar o endereço.

## Escolha do servidor

Para um piloto com poucos usuários, avaliar VPS x86_64 com 2 vCPUs, 4 GB RAM e pelo menos 60 GB de disco. Isso é um ponto de partida, não uma capacidade medida; o modelo de embeddings, Java e PostgreSQL dividem a memória. Preferir 8 GB se o orçamento permitir. Em 4 GB, verificar memória e considerar swap antes de compilar. Compilar um serviço de cada vez.

Em 29/10/2026, a [BoaHost](https://boahost.com.br/vps) anuncia VPS Basic com 2 vCPUs, 4 GB e 60 GB por R$ 49,90/mês. Conferir ciclo mensal e total no carrinho antes de pagar. A indicação considera recursos e preço anunciados; disponibilidade e desempenho não foram testados. O consumo OpenRouter e eventual domínio são adicionais.

## O que já foi preparado

- Containers para interface, backend Java e serviço de IA em CPU, com um único worker.
- PostgreSQL com pgvector e volume persistente.
- Caddy com HTTPS automático e `/api` no mesmo endereço da interface.
- Banco, Java e IA sem portas publicadas na internet.
- Materiais montados somente para leitura e credenciais fora das imagens.
- Criação do índice vetorial após as migrations relacionais, sem baseline automático.

## Etapas para executar com assistência

1. Contratar somente um mês de VPS Linux. Selecionar Ubuntu 24.04 LTS, sem painel pago. Instalar Docker Engine e o plugin Compose conforme a [documentação oficial](https://docs.docker.com/engine/install/ubuntu/).
2. Enviar o código e `neuron-ai/materiais_academicos` para uma pasta privada no servidor. Não enviar ambientes virtuais, caches, pastas temporárias nem os arquivos `.env` do computador.
3. Definir um endereço DNS apontando para o servidor e liberar portas 80/443; restringir o acesso administrativo. Para economizar, avaliar um subdomínio gratuito antes de comprar domínio. O endereço precisa ser real: HTTPS automático não funciona com o exemplo do arquivo.
4. Copiar `deploy/.env.example` para `deploy/.env` **no servidor**. Gerar senha de banco e token interno diferentes e longos. Preencher chave e modelo OpenRouter e dados do primeiro administrador. Não enviar senhas ou chaves pelo chat.
5. Escolher **banco novo** ou **migração do banco local** antes de iniciar. O procedimento abaixo cria uma base nova. Ele não transfere materiais indexados, usuários e conversas do computador.

Na raiz do projeto no servidor:

```sh
docker compose --env-file deploy/.env -f deploy/compose.yaml config --quiet
docker compose --env-file deploy/.env -f deploy/compose.yaml build backend
docker compose --env-file deploy/.env -f deploy/compose.yaml build ai
docker compose --env-file deploy/.env -f deploy/compose.yaml build web
docker compose --env-file deploy/.env -f deploy/compose.yaml up -d
docker compose --env-file deploy/.env -f deploy/compose.yaml ps -a
```

O primeiro início da IA baixa o modelo de embeddings e pode demorar. Seu volume de cache é preservado. As dependências Python ainda não possuem um arquivo de versões fixadas de produção: concluir um build, verificar compatibilidade e fixar as versões antes de estabilizar a instalação.

## Dados e materiais: etapa obrigatória

Uma base nova recebe o catálogo das migrations, mas **não recebe os chunks e embeddings existentes**. A IA não estará pronta para responder só porque os containers iniciaram. Há duas opções:

- Para preservar o ambiente existente: fazer backup privado do PostgreSQL local, verificar a versão, restaurar numa base vazia antes de iniciar o backend e manter o histórico Flyway. Revisar também caminhos de arquivos nos registros para Linux.
- Para uma instalação nova: executar a preparação, indexação e integração das disciplinas conforme os guias de `docs/` e `neuron-ai/`. Os scripts de preparação não são incluídos na imagem de runtime; executar numa etapa de manutenção própria.

Não restaurar backup sobre uma base já usada sem revisão. Não habilitar baseline automático nem apagar volumes para resolver erros de migrations. Materiais precisam existir na pasta montada e seus caminhos no catálogo devem ser compatíveis com `/materiais`.

## Verificação antes da divulgação

Abrir o endereço HTTPS, entrar com o administrador, consultar disciplinas, abrir um PDF e pedir uma resposta de IA com uma fonte verificável. Testar conta de estudante e prática. Reiniciar os serviços e verificar persistência dos dados. Medir memória durante perguntas simultâneas antes de ampliar o público.

Depois do primeiro acesso, remover as duas variáveis de bootstrap do administrador e recriar somente o backend. Visitantes permanecem desativados nesta configuração para controlar o acesso ao consumo da IA. Configurar limite de gasto na conta OpenRouter.

Providenciar backup do PostgreSQL e dos materiais fora da VPS antes do uso real, e testar a restauração. Volumes persistentes não substituem backup. Não usar `docker compose down -v` em uma instalação com dados.

## Estado desta preparação

Os arquivos podem ser revisados sem contratar servidor. A publicação só poderá ser confirmada depois da contratação, configuração do endereço, transferência dos dados e testes externos. A disponibilidade do endpoint `/health` da IA verifica o HTTP, não comprova geração pelo provedor nem a existência do corpus.
