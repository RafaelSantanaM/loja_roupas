-- =========================================================
-- 002_create_produtos_pedidos.sql
-- Cria as tabelas de produtos, pedidos, chaves estrangeiras e índices.
-- =========================================================

CREATE TABLE IF NOT EXISTS produtos (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    preco       NUMERIC(10, 2) NOT NULL CHECK (preco >= 0),
    estoque     INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id           SERIAL PRIMARY KEY,
    cliente_id   INTEGER NOT NULL REFERENCES clientes(id),
    produto_id   INTEGER NOT NULL REFERENCES produtos(id),
    quantidade   INTEGER NOT NULL CHECK (quantidade > 0),
    valor_total  NUMERIC(10, 2) NOT NULL,
    criado_em    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_produto ON pedidos (produto_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON produtos, pedidos TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE produtos_id_seq TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE pedidos_id_seq TO app_loja;

-- Insere produto inicial caso não exista
INSERT INTO produtos (id, nome, preco, estoque)
VALUES (1, 'Camiseta Branca', 49.90, 10)
ON CONFLICT (id) DO NOTHING;
