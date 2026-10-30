# Formatação matemática — publicação em 29/10/2026

Site: https://neuron-45-159-173-74.sslip.io/

A interface publicada utiliza remark-math e KaTeX para frações verticais,
potências, raízes e limites nas mensagens, tabelas e campos de exercícios que
contenham notação matemática delimitada. O Monitor agora recebe orientação
para gerar essa notação e preservar as referências junto às fórmulas.
Texto antigo com divisões escritas usando `/` não é convertido automaticamente.

A interface já havia sido enviada junto da atualização de prática. Esta
publicação complementou somente `neuron-ai/app/rag/monitor_virtual.py` e
reconstruiu o serviço de IA. Banco, contas e históricos não foram alterados
pelo procedimento. A cópia anterior do módulo e a identificação da imagem
anterior estão em `/opt/neuron/deploy/backups/math-20261030T013340Z/`.

Validação: 45 testes de interface; 12 testes e 11 subtestes do Monitor;
compilação de produção; arquivos de matemática acessíveis pelo HTTPS público;
serviço de IA saudável; resposta real para o limite de `(x² − 1)/(x − 1)`
quando `x → 1`, com frações LaTeX, resultado 2 e uma fonte acadêmica.
A consulta de aceitação foi direta ao serviço, sem criar conta ou conversa.

Relatório: `output/verificacao-formatacao-matematica-publicada.json`.
