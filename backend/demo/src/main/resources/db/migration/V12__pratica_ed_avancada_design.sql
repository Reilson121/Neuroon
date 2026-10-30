-- Prática autoral a partir das aulas: não declara existência de prova do professor.
UPDATE disciplina SET possui_prova=TRUE
WHERE slug IN ('estrutura_de_dados_avancada','design_de_artefatos_digitais')
  AND periodo_id IN (SELECT id FROM periodo WHERE numero=3);
