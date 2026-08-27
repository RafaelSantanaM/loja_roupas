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
    ('gerente', '$2b$12$x7a3NfD5y2i2.vqsj9zwvevB.LrooJgAMGEUveD76GJ8.YTHaD7Sq', 'admin'),
    ('vendedor', '$2b$12$x7a3NfD5y2i2.vqsj9zwvevB.LrooJgAMGEUveD76GJ8.YTHaD7Sq', 'funcionario')
ON CONFLICT (username) DO NOTHING;

