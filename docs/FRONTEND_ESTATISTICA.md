# Estatística na interface do NEURON

Integração validada em 28/10/2026 no frontend existente em `frontend/`, adaptado do protótipo. Foram preservados seu layout, logo, histórico do Monitor e avaliação voluntária da plataforma.

## Fluxo disponível

- O catálogo do terceiro período apresenta Estatística e seus 31 assuntos na ordem do cadastro.
- O Monitor recebe disciplina e assunto selecionados, mostra referências com páginas e identifica observações de IA. Conversas anteriores podem ser reabertas na conta do aluno.
- A prática separa questões dos materiais acadêmicos de questões inéditas de IA. Permite selecionar assunto, listas/provas e quantidade.
- As seis questões originais de múltipla escolha mantêm fontes, páginas e numeração. O gabarito da lista continua com autoria oficial não confirmada.
- A geração fica limitada aos seis assuntos contemplados pelas avaliações autorizadas. Os demais assuntos continuam disponíveis no Monitor; ausência de questões mostra estado vazio.
- A correção mostra acerto/erro, alternativa correta, conceito, fórmula quando aplicável, substituição, cálculos, resolução, erros comuns e dica. Resoluções por IA são identificadas.
- Os três materiais aparecem na biblioteca com sua classificação e disponibilidade. Os links de fontes usam a rota pública de arquivos já implementada no backend.

React acessa somente `/api/v1/` no Spring, usando cookies de sessão e CSRF. Spring mantém autenticação, permissões e validações; FastAPI continua interno. Chaves do OpenRouter, chave interna e credenciais do banco não são enviadas ao navegador. Sessões de prática continuam temporárias.

## Ajuste da integração

`frontend/src/hooks/useSessaoPratica.js` coordena as solicitações de prática. Trocar disciplina, assunto ou modo limpa o resultado anterior e cancela a solicitação pendente; respostas atrasadas são ignoradas. Os filtros locais ficam desabilitados durante a preparação. A revisão de questões já vistas depende do botão específico escolhido pelo estudante.

O componente `Pratica` existente reutiliza esse hook; os componentes de questões, correção e Monitor continuam usando os contratos públicos existentes.

## Verificação realizada

- 19 testes de frontend aprovados em seis arquivos, incluindo quatro novos testes de Estatística: envio de filtros, cancelamento ao trocar assunto, revisão explícita de questões vistas e indisponibilidade sem questões artificiais.
- Compilação de produção aprovada com Vite.
- Nove cenários HTTP aprovados através de `http://127.0.0.1:5173`, incluindo login/CSRF, catálogo real, seis questões originais sem gabarito antecipado, correção e reenvio idempotente, estado vazio, geração real pelo OpenRouter, Monitor com referências e histórico e logout.
- Conferência no navegador pela entrada de produção `/`, com conta descartável própria, sem usar `/qa/preview.html`.
- Exercício inédito de quartis exibido e respondido na interface: dados `[3,4,17,19,22]`, convenção R7, `Q1=4`, `Q3=19`, `IQR=15`, alternativa D. Os valores e a unicidade da alternativa correta foram conferidos independentemente da resolução exibida.
- Pergunta enviada pelo navegador: mediana de `[2,4,9,10,100]`. Resposta correta `9`, com referência aos slides nas páginas 30 e 31. O histórico foi reaberto após outra autenticação.
- Prática conferida em celular de 390 × 844, sem rolagem horizontal da página.
- As contagens permaneceram em 193 chunks teóricos, seis origens da lista e nove da prova. A conta temporária e suas mensagens/conversas foram removidas. As permissões dos materiais não foram alteradas nesta etapa.

Durante a validação houve falta de memória no Windows e uma instância antiga do backend deixou requisições pendentes. Os cenários aprovados acima foram repetidos com o backend atualizado respondendo normalmente; tentativas interrompidas não foram contadas como aprovadas.

Relatórios:

- `neuron-ai/saidas_testes/estatistica_validacao_proxy_frontend.json`: aceitação HTTP pela origem da interface. O campo `validacao_visual=false` delimita o escopo desse script.
- `neuron-ai/saidas_testes/estatistica_validacao_frontend.json`: consolidação da conferência visual e dos testes da interface.
- `neuron-ai/saidas_testes/estatistica_validacao_final.json`: validação anterior do backend e do corpus; permanece como registro histórico dessa etapa.

Capturas com dados reais de teste:

- [Prática e correção](validacao-estatistica/pratica-real.png)
- [Prática no celular](validacao-estatistica/pratica-celular.png)
- [Assunto sem questões](validacao-estatistica/assunto-sem-questoes.png)

## Inicialização local

Iniciar cada serviço em um terminal, reutilizando uma instância saudável quando já estiver em execução. As configurações locais permanecem no `.env` ignorado pelo Git.

Na pasta `neuron-ai`:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.servicos_local ia
.\.venv\Scripts\python.exe -B -m scripts.servicos_local backend
```

Na pasta `frontend`:

```text
npm run dev
```

Abrir `http://127.0.0.1:5173/`. Aguardar o carregamento completo da IA antes de usar o Monitor. Não há senha padrão; usar uma conta cadastrada pela administração. O proxy de desenvolvimento encaminha `/api` para Spring em `127.0.0.1:8080`.

Verificações na pasta `frontend`:

```text
npm test -- --pool=threads --maxWorkers=1
npm run build
```

A aceitação HTTP adicional está em `scripts.validar_proxy_frontend_estatistica`, recebe por uma linha JSON via stdin credenciais de uma conta exclusiva `frontend-estatistica-…@example.test` e exige os três serviços iniciados. Ela chama o provedor real e usa créditos, conforme autorização desta tarefa; não executar com contas reais de alunos. A preparação e a remoção da conta são responsabilidade do executor. Nenhuma senha é gravada no relatório.
