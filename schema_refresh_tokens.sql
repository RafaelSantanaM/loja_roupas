-- =========================================================
-- SCHEMA_REFRESH_TOKENS.SQL
-- Guarda os refresh tokens "ativos" de cada usuário. É isso que
-- permite REVOGAR um token antes da hora -- coisa que um JWT
-- sozinho não permite fazer.
-- =========================================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),

    -- "jti" = JWT ID: um identificador único, gerado junto com o token,
    -- que vai DENTRO do próprio JWT. Não guardamos o token inteiro aqui,
    -- só esse "número de série" dele -- é o suficiente para achar e revogar.
    jti         VARCHAR(64) NOT NULL UNIQUE,

    expira_em   TIMESTAMP NOT NULL,
    revogado    BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_jti ON refresh_tokens (jti);

GRANT SELECT, INSERT, UPDATE ON refresh_tokens TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE refresh_tokens_id_seq TO app_loja;
