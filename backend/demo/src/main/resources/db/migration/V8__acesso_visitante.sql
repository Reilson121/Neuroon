-- Visitantes possuem sessão e histórico isolados, sem acesso administrativo.
ALTER TABLE usuario DROP CONSTRAINT IF EXISTS usuario_perfil_check;
ALTER TABLE usuario ADD CONSTRAINT usuario_perfil_check
  CHECK (perfil IN ('ESTUDANTE', 'ADMINISTRADOR', 'VISITANTE'));
