# Monitor conversacional para todas as disciplinas com RAG

O mesmo fluxo atende Estrutura de Dados Avançada, Estatística, Design de
Artefatos Digitais e Projeto de Ideação de Software. Não há memória global
compartilhada entre estudantes nem estado conversacional na instância Python.

## Fluxo

1. O navegador envia a pergunta e o `threadId`, como já fazia.
2. Spring verifica conta, dono da conversa, disciplina e assunto; busca as
   oito mensagens mais recentes em ordem cronológica (até 2000 caracteres
   por mensagem). O cliente não fornece nem escolhe esse histórico.
3. A IA usa esse trecho recente para transformar referências como “isso”,
   “explique melhor” e “mais visual” em uma consulta acadêmica independente.
   Mudanças explícitas de tema devem prevalecer sobre o tema anterior.
4. A recuperação consulta novamente os materiais com os mesmos filtros e
   permissões atuais. Fontes de respostas antigas não são reaproveitadas como
   autorização ou evidência. Material revogado continua bloqueado.
5. A geração recebe a pergunta atual, o histórico recente e as novas fontes.
   Pode adaptar a linguagem, construir analogias e exemplos e mostrar tabelas
   ou esquemas ASCII. Exemplos novos são identificados como criados pela IA;
   a citação aponta ao conceito de base, sem atribuir o exemplo ao professor.
6. O texto e as fontes atuais são salvos no histórico existente. Ao reabrir a
   conversa, a continuidade também é reaberta.

Sem contexto acadêmico suficiente, o sistema continua recusando inventar uma
resposta fundamentada. Se a referência conversacional não puder ser resolvida,
pede ao aluno o tema (`tema_nao_identificado`). O contexto é uma janela recente,
não memória ilimitada de todas as conversas do usuário.

As mensagens antigas são dados não confiáveis, não instruções do sistema nem
fontes acadêmicas. O backend não acrescenta chaves, emails, identificadores de
conta ou metadados de autenticação ao contexto. O envio utiliza o provedor de IA
já configurado no serviço. Uma continuação acrescenta uma chamada curta para
resolver o contexto (300 tokens, timeout 15 s); a geração permanece limitada
a 2600 tokens e até duas reformulações, com timeout de 30 s por chamada.

## Contrato interno

O campo opcional `historico` de `POST /internal/v1/chat` é uma lista de até
oito objetos `{papel: USUARIO|MONITOR, conteudo: texto}`. Texto obrigatório,
máximo de 2000 caracteres e campos extras recusados. A API pública continua
igual, sem aceitar histórico arbitrário enviado pelo navegador.

Blocos de código/esquemas preservam linhas vazias. Uma referência logo após
um bloco é associada a ele antes da remoção de conteúdo sem citação. Referências
inexistentes continuam invalidando a resposta; o verificador não cria fontes.
Na geração atual, exemplos visuais são devolvidos separadamente no JSON do
modelo, em `visuais: [{markdown, fontes}]`. A aplicação exige IDs reais de fontes
do conceito, identifica a autoria didática da IA e monta a apresentação com
esses IDs. Isso evita perder o desenho quando o modelo cita apenas a legenda
ou o parágrafo que o explica. Visuais com fontes desconhecidas são recusados.
O contrato público continua devolvendo texto Markdown e os metadados das fontes.
Se o aluno pediu uma explicação visual e a saída contém só prosa, há no máximo
um reparo de formato com as mesmas fontes (1200 tokens, timeout 10 s). Persistindo
a omissão, a aplicação não apresenta a resposta como visual concluída.

## Verificação

- Backend: isolamento entre contas e assuntos, ordem e limite das oito
  mensagens, truncamento de textos extensos e integração com a preparação do chat.
- IA: continuação no componente das quatro disciplinas, mudança de tema,
  requisições sem histórico independentes, fonte revogada/ausente, necessidade
  de esclarecimento, contrato da API e preservação de diagramas com fontes.
- Aceitação real: `python -B -m scripts.validar_conversa_rag`, com IA local
  iniciada. Faz perguntas acadêmicas, pedidos de explicação visual e de novos
  exemplos nas quatro disciplinas, e uma pergunta independente fora dos materiais.
  Consome créditos no provedor configurado e não grava conversas na conta do
  estudante. Resultado em `neuron-ai/saidas_testes/validacao_conversa_rag.json`.

O frontend já envia `threadId` nas continuações e renderiza Markdown, tabelas e
código; não precisa enviar o histórico pelo navegador nem acessar a IA diretamente.
Este ajuste não cadastra novas disciplinas ou materiais no catálogo relacional.

## Resultado verificado em 28/10/2026

- 34 testes do Spring, 117 testes da IA e 14 testes da interface aprovados;
  pacote Java gerado e ativado localmente.
- 16 cenários reais aprovados nas quatro disciplinas: pergunta inicial,
  continuação didática/visual, outro exemplo criado pela IA e pergunta
  independente sem cobertura nos materiais. Nenhuma falha no relatório final.
- Percurso público validado com conta temporária: Spring envia o contexto,
  a segunda pergunta recebe resposta visual fundamentada na mesma conversa,
  e as quatro mensagens/fontes podem ser reabertas. Conta de teste removida.
- Conferência pela interface na conta local de prévia: nova conversa
  `O que são pilhas?` seguida de pedido visual entregou tabela, esquema textual
  e referência à Aula 0, página 14. Conversa demonstrativa mantida no histórico.
  O rascunho anterior do usuário foi preservado sem envio.
- Os 955 chunks das quatro disciplinas foram preservados (363 Design,
  208 Estatística, 167 ED e 217 Ideação). Não houve reingestão dos arquivos.

Relatórios: `saidas_testes/validacao_conversa_rag.json` e
`saidas_testes/validacao_backend_contexto.json`, dentro de `neuron-ai`.
As amostras validam a integração e o comportamento observado; não constituem
garantia de correção acadêmica de todas as respostas futuras do modelo.
