CREATE TABLE conversa_monitor (
 id UUID PRIMARY KEY,
 usuario_id BIGINT NOT NULL REFERENCES usuario(id),
 disciplina_id BIGINT NOT NULL REFERENCES disciplina(id),
 assunto_id BIGINT,
 titulo VARCHAR(100) NOT NULL,
 criado_em TIMESTAMP WITH TIME ZONE NOT NULL,
 atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL,
 FOREIGN KEY(assunto_id,disciplina_id) REFERENCES assunto(id,disciplina_id)
);
CREATE TABLE mensagem_monitor (
 id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 conversa_id UUID NOT NULL REFERENCES conversa_monitor(id),
 papel VARCHAR(12) NOT NULL CHECK(papel IN ('USUARIO','MONITOR')),
 conteudo TEXT NOT NULL,
 fontes TEXT NOT NULL DEFAULT '[]',
 criado_em TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX ix_conversa_monitor_usuario ON conversa_monitor(usuario_id,disciplina_id,atualizado_em DESC);
CREATE INDEX ix_mensagem_monitor_conversa ON mensagem_monitor(conversa_id,id);
