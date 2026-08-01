-- =========================================================
-- SCHEMA_USUARIOS.SQL
-- Tabela de usuários que podem fazer LOGIN na API.
-- Isso é diferente de "clientes" -- clientes são os dados da
-- loja, "usuarios" são quem tem permissão de mexer na API
-- (ex: os funcionários da loja).
-- =========================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id           SERIAL PRIMARY KEY,
    username     VARCHAR(50) NOT NULL UNIQUE,

    -- NUNCA guardamos a senha em texto puro aqui!
    -- Guardamos só o HASH dela (o "resultado moído", sem volta).
    senha_hash   VARCHAR(255) NOT NULL,

    -- RBAC: o "crachá" do usuário. Só aceita esses dois valores.
    papel        VARCHAR(20) NOT NULL DEFAULT 'funcionario'
                 CHECK (papel IN ('admin', 'funcionario')),

    criado_em    TIMESTAMP NOT NULL DEFAULT NOW()
);

GRANT SELECT, INSERT ON usuarios TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE usuarios_id_seq TO app_loja;
