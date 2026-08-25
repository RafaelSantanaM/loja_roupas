-- =========================================================
-- 003_create_usuarios.sql
-- Cria a tabela de usuários com suporte a RBAC (papeis: admin, funcionario).
-- =========================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id           SERIAL PRIMARY KEY,
    username     VARCHAR(50) NOT NULL UNIQUE,
    senha_hash   VARCHAR(255) NOT NULL,
    papel        VARCHAR(20) NOT NULL DEFAULT 'funcionario'
                 CHECK (papel IN ('admin', 'funcionario')),
    criado_em    TIMESTAMP NOT NULL DEFAULT NOW()
);

GRANT SELECT, INSERT, UPDATE ON usuarios TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE usuarios_id_seq TO app_loja;

-- Usuários padrão para testes e desenvolvimento (senha: 'senha123')
INSERT INTO usuarios (username, senha_hash, papel)
VALUES 
    ('gerente', '$2b$12$K1rZc0Jt8iVv42aN5zZ3m.r6Y4n/2uT5X7g5b6C7d8e9f0a1b2c3d', 'admin'),
    ('vendedor', '$2b$12$K1rZc0Jt8iVv42aN5zZ3m.r6Y4n/2uT5X7g5b6C7d8e9f0a1b2c3d', 'funcionario')
ON CONFLICT (username) DO NOTHING;
