# Conferência visual

Com o servidor de desenvolvimento ativo, abra `/qa/preview.html` para conferir
o layout com dados explicitamente fictícios, sem acessar banco ou provedor de IA.
O histórico e as respostas dessa página são simulações usadas apenas nesta
validação visual. A entrada de produção continua sendo `index.html`, com a API real.

Conferir: início, disciplinas, Monitor Virtual (histórico e fontes), prática,
materiais e avaliação da plataforma, em larguras de 320, 390, 768, 1024 e 1440 pixels. No celular, verificar
o menu inferior, a abertura/fechamento do histórico, o teclado e o botão de envio.

Na avaliação, escolher de 1 a 5 estrelas, enviar com ou sem comentário,
reabrir pelo menu e atualizar a resposta. A simulação fica apenas em memória
até recarregar esta página; os testes do servidor verificam a gravação real.

O catálogo de disciplinas, assuntos e metadados dos materiais vem de
`catalogo.json`, uma fotografia do banco local conferida em 29/10/2026.
Ele contém Sistemas Digitais no segundo período e quatro disciplinas no terceiro,
com 31 assuntos de Estatística e cinco de Projeto de Ideação de Software. A prévia respeita os
vínculos de período e disciplina; não inventa um quarto período com as mesmas disciplinas.
Os PDFs autenticados, a IA e as contas reais continuam fora desta simulação.
Para atualizar a fotografia, execute, na raiz de NEURON, com o banco disponível:
`neuron-ai/.venv/Scripts/python.exe tmp/auditar_catalogo_previa.py`.
O script faz consultas somente de leitura e exporta apenas metadados acadêmicos.
