# Interface e histórico do Monitor Virtual

A interface segue as cores e a estrutura do protótipo: navegação lateral
azul-marinho, cartões claros, início, disciplinas e área de estudo. O logotipo
fornecido está em `frontend/public/neuron-logo.png`, preservado sem alteração;
o componente Logo enquadra as margens transparentes apenas na apresentação.

## Responsividade

- Computador: navegação lateral e histórico ao lado do chat.
- Tablet: distribuição adaptável dos cartões e seletores.
- Celular: navegação inferior, cartões em uma coluna e histórico aberto pelo
  botão do chat. Escape ou Fechar histórico retorna à conversa.
- O campo de mensagem usa Enter para enviar e Shift+Enter para uma nova linha.
  A rolagem automática fica restrita às mensagens.
- Há foco visível, rótulos de formulário, link para pular ao conteúdo e respeito
  à preferência de movimento reduzido.

## Histórico

A migration `V3__historico_monitor_virtual.sql` cria as tabelas de conversas e
mensagens. O Flyway aplica essa migration na próxima inicialização do backend.
As conversas pertencem ao usuário autenticado e ficam separadas por disciplina
e assunto. São armazenadas perguntas, respostas, datas e metadados das fontes.
As duas mensagens de cada troca são gravadas em uma única transação, depois de
uma resposta válida do serviço de IA, antes da confirmação ao navegador.

- `GET /api/v1/monitor/conversas?disciplinaId=…&assuntoId=…`: últimas 50 conversas
  do contexto selecionado. O assunto é opcional; sem ele, lista as conversas
  gerais da disciplina.
- `GET /api/v1/monitor/conversas/{id}`: mensagens da conversa, apenas para seu dono.
- `POST /api/v1/monitor/chat`: reutiliza `threadId` para acrescentar uma troca.
  O evento `done` devolve o identificador salvo.
- Nova conversa limpa a área de escrita; as conversas anteriores continuam
  disponíveis. Cada conversa comporta até 100 trocas.

O histórico permite reler e agrupar as trocas. A etapa inicial respondia cada
pergunta isoladamente. Agora, as oito mensagens mais recentes da mesma conversa
também contextualizam a pergunta, e as fontes são recuperadas novamente no
contexto selecionado. Veja `CHAT_CONVERSACIONAL_RAG.md`.

Monitoria humana, mensagens com monitores humanos e agendamentos continuam fora
do escopo.

## Avaliação da plataforma

O menu dos estudantes inclui **Avaliar plataforma** (ou **Avaliar** no celular).
A avaliação é voluntária e não bloqueia acesso a conteúdos, chat ou prática.
A nota de 1 a 5 estrelas é obrigatória para enviar; o comentário é opcional e
comporta até 2000 caracteres. O aluno pode reabrir e atualizar sua avaliação.

A funcionalidade usa a tabela `feedback_plataforma`, já criada pela migration
V1, sem precisar de uma nova migration. A conta é obtida da autenticação; o
navegador não escolhe o autor da avaliação. O envio exige CSRF e perfil de
estudante. O bloqueio transacional da conta serializa envios simultâneos para
evitar novas avaliações duplicadas. Registros históricos existentes são
preservados; a interface consulta e atualiza o mais recente da conta.

- `GET /api/v1/avaliacao-plataforma/minha`: avaliação do aluno autenticado ou 204
  quando ele ainda não avaliou.
- `PUT /api/v1/avaliacao-plataforma/minha`: salva ou atualiza a avaliação.

Os comentários não são publicados para outros alunos. A página de prévia usa
um registro fictício em memória, separado da API real.

## Verificação

Os testes do servidor cobrem persistência, ordem das mensagens, preservação das
fontes, separação de assuntos e bloqueio de acesso por outra conta. Os testes da
interface cobrem reabertura, várias mensagens, falha de envio e histórico móvel,
além dos testes existentes de prática.

A página de desenvolvimento `/qa/preview.html` usa dados fictícios para conferir
o layout sem depender de banco ou IA. Ela não é uma entrada da compilação de
produção. As capturas em `docs/preview-front/` foram feitas nessa página.

Conferidas as seções Início, Disciplinas, Monitor Virtual, Praticar e Materiais
nas larguras de 320, 768, 1024 e 1440 pixels, sem rolagem horizontal da página.
O chat também foi conferido em 390 × 844, incluindo reabertura e envio.

Comandos de verificação:

```text
frontend: npm test -- --pool=threads --maxWorkers=1
frontend: npm run build
backend/demo: gradlew.bat test -PjavaVersion=23
```

O parâmetro de versão Java apenas seleciona o JDK local disponível; o projeto
continua compilando o código com alvo Java 17.
