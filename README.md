# NEURON — Como executar o que já está pronto: Projeto de Ideação de Software

Guia para rodar, passo a passo, tudo o que já foi implementado para a disciplina **Projeto de Ideação de Software** (3º período) no serviço de IA `neuron-ai`.

> Este guia foi escrito a partir do código do projeto (`app/`, `scripts/`, `saidas_testes/`). Os números de "resultado esperado" vêm dos arquivos de saída já salvos em `saidas_testes/`. O que **não** foi verificado está marcado como tal.

---

## 1. O que existe para esta disciplina

Material em `materiais_academicos/periodo_03/projeto_de_ideacao_de_software/`, com 5 PDFs (professora Jeneffer Cristine Ferreira):

| Pasta | Aula |
|---|---|
| `aula_01_introducao` | Aula 01 — Introdução |
| `aula_02_lean_canvas` | Aula 02 — Lean Canvas |
| `aula_03_historias_de_usuario` | Aula 03 — Histórias de Usuário |
| `aula_04_mapa_de_navegacao_e_wireframe` | Aula 04 — Mapa de Navegação e Wireframe |
| `aula_05_matriz_csd` | Aula 05 — Matriz CSD |

Etapas do pipeline já implementadas e os scripts que as testam:

| Etapa | Script | Chama a API (custo)? |
|---|---|---|
| 0. Conferir os 5 PDFs | `scripts/test_disciplina_ideacao.py` | Não |
| 1. Diagnóstico textual × multimodal | `scripts/test_ideacao_detector.py` | Não |
| 2. Teste controlado (15 páginas) | `scripts/test_ideacao_amostra.py` | **Sim**, nas páginas multimodais |
| 3. Chunking da amostra | `scripts/test_chunk_processor.py` | Não |
| 4. Pipeline completa da Aula 03 | `scripts/test_pipeline_aula03.py` | **Sim**, nas páginas multimodais |
| 5. Embeddings + busca semântica | `scripts/test_embeddings_aula03.py` | Não |
| 6. Demo RAG completo (em memória) | `scripts/test_rag_demo_aula03.py` | **Sim**, 1 chamada ao LLM por pergunta |

Por enquanto, as etapas 4 a 6 usam **somente a Aula 03**. As aulas 1, 2, 4 e 5 passam apenas pelas etapas 0 a 3 (diagnóstico e amostra).

---

## 2. Pré-requisitos

- Windows com PowerShell.
- Python (os arquivos compilados do projeto indicam Python 3.13).
- Pasta do projeto: `C:\Projeto Extensionista 2\NEURON\neuron-ai`
- Ambiente virtual: `C:\Projeto Extensionista 2\NEURON\neuron-ai\.venv`
- Conta no OpenRouter com chave de API (necessária apenas nas etapas que chamam a API).

### 2.1 Ativar o ambiente virtual

```powershell
cd "C:\Projeto Extensionista 2\NEURON\neuron-ai"
.\.venv\Scripts\Activate.ps1
```

O prompt deve passar a mostrar `(.venv)`. Se o PowerShell bloquear a ativação por política de execução, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 2.2 Arquivo `.env`

Na raiz de `neuron-ai` deve existir um arquivo `.env` com:

```
OPENROUTER_API_KEY=sua_chave_aqui
```

Opcional: `OPENROUTER_MODEL=...` (se não for definido, o código usa `deepseek/deepseek-v4-flash-0731`).

Segurança:

- Nunca envie o `.env` por chat, e-mail ou Git.
- Confirme que `.env` está no `.gitignore`.
- Se a chave vazar, revogue-a no painel do OpenRouter e gere outra.

### 2.3 Dependências

O zip não trazia `requirements.txt`. Pelos `import` do código, o projeto usa estas bibliotecas:

`fastapi`, `uvicorn`, `python-dotenv`, `openai`, `langchain-openrouter`, `langchain-community`, `langchain-text-splitters`, `pypdf`, `pymupdf`, `python-pptx`, `sentence-transformers`, `numpy`.

Como o ambiente `.venv` já foi usado nos testes, elas já devem estar instaladas. Para conferir:

```powershell
pip list
```

Se quiser registrar as versões exatas que funcionam hoje (recomendado):

```powershell
pip freeze > requirements.txt
```

### 2.4 Primeira execução dos embeddings

Na primeira vez que o modelo `paraphrase-multilingual-MiniLM-L12-v2` é usado, ele é baixado da internet. Isso é normal e acontece uma única vez; depois fica em cache.

---

## 3. Execução passo a passo

Todos os comandos abaixo devem ser executados **na pasta `neuron-ai`**, com o `.venv` ativo. Use sempre o formato `python -m scripts.NOME` (sem `.py`).

### Etapa 0 — Conferir os materiais (sem custo)

```powershell
python -m scripts.test_disciplina_ideacao
```

**Esperado:** lista dos PDFs encontrados e a mensagem `OK: os 5 materiais foram encontrados.`

Se aparecer `ATENCAO`, confira se os PDFs estão nas pastas `aula_01...` a `aula_05...` descritas na seção 1.

### Etapa 1 — Diagnóstico textual × multimodal (sem custo)

```powershell
python -m scripts.test_ideacao_detector
```

Para cada PDF, mostra o total de páginas, quantas são textuais, quantas são candidatas a multimodal e quais são. Usa só o detector local; **não chama a API**.

### Etapa 2 — Teste controlado de 15 páginas (chama a API)

```powershell
python -m scripts.test_ideacao_amostra
```

Testa 3 páginas de cada aula (15 no total). Páginas sem texto extraível ou muito visuais vão para o modelo multimodal (OpenRouter); as demais usam extração textual.

**Resultado já salvo** em `saidas_testes/ideacao_amostra_resultado.json`: 15 páginas, sendo 13 multimodais e 2 textuais. Rodar de novo gera custo e **sobrescreve** esse arquivo.

### Etapa 3 — Chunking da amostra (sem custo)

```powershell
python -m scripts.test_chunk_processor
```

Lê `saidas_testes/ideacao_amostra_resultado.json`, divide em chunks (`chunk_size=1000`, `chunk_overlap=150`) e salva em `saidas_testes/ideacao_amostra_chunks.json`.

**Resultado já salvo:** 18 chunks a partir das 15 páginas. Depende do arquivo da etapa 2; se ele não existir, o script avisa e encerra.

### Etapa 4 — Pipeline completa da Aula 03 (chama a API)

```powershell
python -m scripts.test_pipeline_aula03
```

Processa o PDF inteiro da Aula 03 (Histórias de Usuário): extrai as páginas, aplica o detector, usa o modelo multimodal quando necessário, gera os chunks com metadados e salva em `saidas_testes/aula_03_pipeline_completa.json`.

**Resultado esperado (conforme o arquivo já salvo):**

| Item | Valor |
|---|---|
| Total de páginas | 12 |
| Páginas textuais | 10 |
| Páginas multimodais | 2 |
| Chunks gerados | 12 |
| Chunk size / overlap | 1000 / 150 |

Esta etapa **gera o arquivo que as etapas 5 e 6 usam**. Se `aula_03_pipeline_completa.json` já existe, não é preciso rodá-la de novo (evita custo).

### Etapa 5 — Embeddings e busca semântica (sem custo)

```powershell
python -m scripts.test_embeddings_aula03
```

Gera os embeddings (384 dimensões, normalizados) dos 12 chunks e busca os 3 mais parecidos com a pergunta:

> *Qual é a estrutura básica de uma história de usuário?*

**Esperado:** os resultados do Top 3 devem ser semanticamente relevantes, incluindo o chunk da página 3 com a estrutura "Como um [tipo de usuário] / Eu quero [objetivo] / Para que [benefício]".

### Etapa 6 — Demo do Monitor Virtual, em memória (chama a API)

Fluxo: `pergunta → embedding → Top-K → DeepSeek → resposta + fontes`.

```powershell
python -m scripts.test_rag_demo_aula03
```

Com a pergunta padrão (a mesma da etapa 5). Para fazer outra pergunta:

```powershell
python -m scripts.test_rag_demo_aula03 "Por que histórias de usuário são importantes?"
```

Para testar a **ausência de evidência** (pergunta fora do material):

```powershell
python -m scripts.test_rag_demo_aula03 "Qual é a capital da França?"
```

O que o script faz (conforme o código):

1. Carrega os 12 chunks de `saidas_testes/aula_03_pipeline_completa.json`.
2. Gera os embeddings e busca os `TOP_K = 3` chunks mais similares.
3. Se a melhor similaridade ficar abaixo de `SIMILARIDADE_MINIMA = 0.25`, **não chama o LLM** e responde com a mensagem de fallback.
4. Caso contrário, envia a pergunta + trechos ao modelo, que deve responder **somente** com base no contexto.
5. Imprime a resposta e as **fontes** (aula, assunto, página, tipo de extração, similaridade e `chunk_id`), vindas dos **metadados** dos chunks, não do texto do LLM.
6. Se o modelo disser que os trechos não bastam, as fontes não são exibidas.

Observações importantes:

- O valor `0.25` é um **palpite inicial, ainda não calibrado**. O próprio script recomenda ajustá-lo olhando as similaridades impressas.
- Não consegui executar este script aqui (sem a chave de API e sem o modelo de embeddings), então o comportamento da pergunta da França **ainda precisa ser confirmado por você**. Se ela for respondida em vez de cair no fallback, ajuste `SIMILARIDADE_MINIMA` (ou o prompt) e me envie a saída.

---

## 4. Teste opcional: conexão com o LLM

Para verificar apenas se a chave e o modelo do OpenRouter estão funcionando:

```powershell
python -m scripts.test_llm
```

**Esperado:** o modelo responde algo como "conexão do NEURON com o DeepSeek funcionando."

---

## 5. Arquivos gerados (`saidas_testes/`)

| Arquivo | Gerado por | Conteúdo |
|---|---|---|
| `ideacao_amostra_resultado.json` | `test_ideacao_amostra` | 15 páginas extraídas (13 multimodais, 2 textuais) |
| `ideacao_amostra_chunks.json` | `test_chunk_processor` | 18 chunks da amostra |
| `aula_03_pipeline_completa.json` | `test_pipeline_aula03` | Resumo, páginas e 12 chunks da Aula 03 |

Metadados de cada chunk (conforme o JSON salvo): `chunk_id`, `periodo`, `disciplina`, `assunto`, `aula`, `arquivo`, `pagina`, `tipo_arquivo`, `tipo_extracao`, `motivos_deteccao`, `pasta_aula`, `chunk_index`, `total_chunks_pagina`, `chunk_caracteres`, entre outros.

---

## 6. Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `ModuleNotFoundError: No module named 'app'` | Comando executado fora da pasta `neuron-ai` ou sem `-m` | Entre em `neuron-ai` e use `python -m scripts.NOME` |
| `ModuleNotFoundError` de outra biblioteca | Pacote não instalado no `.venv` | Confirme que o `.venv` está ativo e instale o pacote com `pip install` |
| `OPENROUTER_API_KEY não encontrada no .env` | `.env` ausente, no lugar errado ou sem a variável | Crie/ajuste o `.env` na raiz de `neuron-ai` |
| `FileNotFoundError: Arquivo de chunks não encontrado` | Etapa 4 ainda não foi executada | Rode `python -m scripts.test_pipeline_aula03` |
| Acentos quebrados no PowerShell | Codificação do terminal | A demo já força UTF-8; nos outros scripts, rode `chcp 65001` antes |
| Primeira execução lenta nos embeddings | Download do modelo | Aguardar; acontece só uma vez |
| Erro 401/402/429 do OpenRouter | Chave inválida, sem crédito ou limite de uso | Confira a chave e o saldo no painel do OpenRouter |

---

## 7. O que ainda não está pronto

- Persistência dos chunks e embeddings no **PostgreSQL + pgvector** (a demo atual é em memória).
- Calibração do limiar de similaridade (`SIMILARIDADE_MINIMA`).
- Pipeline completa (chunks + embeddings + demo) para as aulas 1, 2, 4 e 5.
- Retriever com filtros por disciplina/assunto e integração com o Spring Boot (`/internal/v1`).
