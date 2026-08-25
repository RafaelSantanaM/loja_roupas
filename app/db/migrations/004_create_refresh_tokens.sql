-- =========================================================
-- 004_create_refresh_tokens.sql
-- Cria a tabela de refresh tokens para suporte a revogação de sessão.
-- =========================================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    jti         VARCHAR(64) NOT NULL UNIQUE,
    expira_em   TIMESTAMP NOT NULL,
    revogado    BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_jti ON refresh_tokens (jti);

GRANT SELECT, INSERT, UPDATE ON refresh_tokens TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE refresh_tokens_id_seq TO app_loja;
