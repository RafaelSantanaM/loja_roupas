-- =========================================================
-- 001_create_clientes.sql
-- Cria a tabela de clientes, seus índices e permissões.
-- =========================================================

CREATE TABLE IF NOT EXISTS clientes (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    telefone        VARCHAR(20),
    data_nascimento DATE,
    endereco        TEXT,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes (email);

-- Cria o usuário da aplicação caso não exista
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_loja') THEN
        CREATE ROLE app_loja WITH LOGIN PASSWORD 'LOGIN123';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE loja_roupas TO app_loja;
GRANT SELECT, INSERT, UPDATE, DELETE ON clientes TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE clientes_id_seq TO app_loja;
