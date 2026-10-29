-- Correção do período curricular sem alterar IDs, PDFs, conversas ou embeddings.
INSERT INTO periodo(numero,nome,ordem)
VALUES(2,'2º período',2) ON CONFLICT(numero) DO NOTHING;

UPDATE disciplina SET periodo_id=(SELECT id FROM periodo WHERE numero=2),
 atualizado_em=CURRENT_TIMESTAMP WHERE slug='sistemas_digitais';

-- O índice é opcional em uma instalação somente do catálogo relacional.
DO $$
BEGIN
 IF to_regclass('public.chunk_documento') IS NOT NULL THEN
  UPDATE chunk_documento SET periodo='02',
   periodo_id=(SELECT id FROM periodo WHERE numero=2)
   WHERE disciplina='sistemas_digitais';
 END IF;
END $$;
