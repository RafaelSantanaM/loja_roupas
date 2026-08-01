-- =========================================================
-- SCHEMA_PEDIDOS.SQL
-- Exercício: adicionar "produtos" e "pedidos", relacionados
-- com a tabela "clientes" que já existe.
--
-- Rode este arquivo DEPOIS do schema.sql original:
--   psql -U postgres -d loja_roupas -f schema_pedidos.sql
-- =========================================================

-- Tabela de produtos da loja (ex: camisetas, calças...)
CREATE TABLE IF NOT EXISTS produtos (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    preco       NUMERIC(10, 2) NOT NULL CHECK (preco >= 0),
    estoque     INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)
);

-- Tabela de pedidos: o "link" entre um cliente e um produto
CREATE TABLE IF NOT EXISTS pedidos (
    id           SERIAL PRIMARY KEY,

    -- Chave estrangeira (FOREIGN KEY): aponta pra um cliente que já existe.
    -- Se o cliente for apagado, o Postgres AVISA e impede (padrão RESTRICT),
    -- pra não deixar um pedido "órfão", sem dono.
    cliente_id   INTEGER NOT NULL REFERENCES clientes(id),

    -- Aponta pra um produto que já existe
    produto_id   INTEGER NOT NULL REFERENCES produtos(id),

    quantidade   INTEGER NOT NULL CHECK (quantidade > 0),
    valor_total  NUMERIC(10, 2) NOT NULL,
    criado_em    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices para buscas comuns: "todos os pedidos de um cliente"
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_produto ON pedidos (produto_id);

-- Dá permissão pro usuário de trabalho mexer nas tabelas novas também
GRANT SELECT, INSERT, UPDATE, DELETE ON produtos, pedidos TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE produtos_id_seq TO app_loja;
GRANT USAGE, SELECT ON SEQUENCE pedidos_id_seq TO app_loja;

-- Um produto de exemplo pra testar o exercício
INSERT INTO produtos (nome, preco, estoque) VALUES ('Camiseta Branca', 49.90, 3);
