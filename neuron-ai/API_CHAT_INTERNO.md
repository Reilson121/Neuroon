# Chat interno — primeira versão JSON

`POST /internal/v1/chat` é a interface do serviço Python para o Spring Boot.
Reutiliza o `MonitorVirtual` validado, incluindo recuperação por disciplina,
assunto opcional, fontes e até duas reformulações. Não grava histórico de chat.

## Requisição

```json
{
  "pergunta": "Como funciona a rotação zig-zag em uma árvore AVL?",
  "disciplina": "estrutura_de_dados_avancada",
  "assunto": "arvores_balanceadas_e_avl"
}
```

- `pergunta`: obrigatória, texto não vazio, até 4000 caracteres.
- `disciplina`: obrigatória, slug de até 150 caracteres.
- `assunto`: opcional ou `null`; quando preenchido, slug de até 150 caracteres.
- `historico`: opcional, até oito mensagens `{papel: USUARIO|MONITOR, conteudo}`,
  com até 2000 caracteres cada, obtidas pelo Spring após verificar dono e contexto.
  Veja `../docs/CHAT_CONVERSACIONAL_RAG.md`. O serviço Python permanece sem
  persistência de conversas e refaz a recuperação das fontes a cada pergunta.
- Slugs usam letras minúsculas sem acentos, números e sublinhados entre palavras.
- Espaços nas extremidades são removidos. Campos desconhecidos são recusados.
- Os limites são técnicos desta primeira versão; o contrato deve ser alinhado
  com o Spring Boot antes da integração. Os IDs relacionais ainda não substituem
  os slugs usados pelo índice existente.

## Resposta de sucesso — HTTP 200

Exemplo ilustrativo do formato; os textos e metadados reais vêm do Monitor:

```json
{
  "resposta": "Faça a rotação à esquerda no filho e à direita no pai. [F1]",
  "fontes": [
    {
      "referencia": "F1",
      "chunk_id": "identificador-do-chunk",
      "arquivo": "Aula_2.pdf",
      "pagina": 90,
      "assunto": "arvores_balanceadas_e_avl",
      "aula": "02",
      "similaridade": 0.7,
      "disciplina": "estrutura_de_dados_avancada",
      "periodo": "03",
      "tipo_arquivo": "pdf",
      "tipo_extracao": "multimodal"
    }
  ],
  "fallback": false,
  "motivo": null,
  "reformulacoes": 1,
  "blocos_sem_fonte_removidos": 0
}
```

Os campos adicionais das fontes são preservados, incluindo `paginas_mescladas`,
`chunk_index`, IDs e demais metadados do RAG. A API não devolve embeddings nem
acrescenta trechos completos à resposta: devolve os metadados citados pelo Monitor.

Ausência de contexto continua sendo HTTP 200, com `fallback=true`, `fontes=[]`
e `motivo=sem_contexto` ou `contexto_insuficiente`. Falhas de formato, referências
ou geração incompleta tratadas pelo Monitor também têm `fallback=true`, mas
retornam uma mensagem de falha de geração e seu motivo próprio. A interface
pode distinguir esses casos sem apresentar uma indisponibilidade como resposta
acadêmica.

## Erros HTTP

```json
{
  "detail": {
    "codigo": "BASE_INDISPONIVEL",
    "mensagem": "A base de materiais está temporariamente indisponível."
  }
}
```

| HTTP | Código | Situação |
|---|---|---|
| 422 | `REQUISICAO_INVALIDA` | JSON inválido, campo obrigatório ausente, tipo ou formato incorreto; inclui a lista `campos` |
| 502 | `IA_ERRO_PROVEDOR` | Provedor de IA devolveu erro |
| 503 | `BASE_INDISPONIVEL` | Falha de acesso ao PostgreSQL |
| 503 | `IA_INDISPONIVEL` | Falha de conexão ou limite do provedor de IA |
| 503 | `MONITOR_INDISPONIVEL` | Inicialização/configuração indisponível |
| 504 | `IA_TIMEOUT` | Provedor excedeu o tempo de resposta |
| 500 | `ERRO_INTERNO` | Outra falha interna ou resposta fora do contrato |

Mensagens de exceções externas, detalhes de conexão e valores das entradas
inválidas não são refletidos nas respostas nem registrados pela rota.

## Inicialização e execução local

O Monitor é criado na primeira requisição válida e reutilizado por processo.
`/health` e `/openapi.json` funcionam sem carregar embeddings nem abrir conexão
com o banco. O `/health` indica que o serviço HTTP está ativo; não confirma a
disponibilidade do PostgreSQL ou do provedor de IA.

```powershell
Set-Location 'C:\Projeto Extensionista 2\NEURON\neuron-ai'
& '.\.venv\Scripts\python.exe' -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Documentação local do contrato: `http://127.0.0.1:8000/docs`.
O endereço de escuta acima fica restrito ao computador local. O navegador da
aplicação deve continuar consumindo apenas o Spring Boot; não foi habilitado CORS.
Em deploy, o serviço Python deve ficar na rede interna acessível ao Spring.
Autenticação, autorização e rate limit dos estudantes permanecem no Spring Boot.
Não foi escolhida uma estratégia adicional de autenticação entre serviços.

## Validação

Validação executada em 27/10/2026: **46 testes aprovados na suíte atual**,
incluindo **9 testes específicos da API e da inicialização do Monitor**.

```powershell
& '.\.venv\Scripts\python.exe' -B -m unittest discover -s test -p 'test_*.py' -v
```

Os testes HTTP usam o aplicativo FastAPI e dependências simuladas; verificam
validação, filtros, preservação de metadados, fallback, códigos de erro,
reutilização da instância e o fluxo HTTP → Monitor real → reformulação → fontes
com banco/modelo simulados. Esses testes não enviam materiais ao OpenRouter.
O RAG com banco/modelo reais já foi validado separadamente; não se afirma um
novo teste HTTP com OpenRouter real nesta etapa.

Streaming SSE, integração com o `AiClient` do Spring Boot e autenticação entre
serviços ainda são etapas seguintes. Este endpoint retorna JSON após a geração
completa; ele não emite eventos `token`, `sources` e `done`.
