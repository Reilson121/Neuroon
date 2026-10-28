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
