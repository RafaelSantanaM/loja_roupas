-- =========================================================
-- SCHEMA.SQL
-- Este arquivo cria: o banco de dados, a tabela de clientes
-- e um "usuário de segurança" que só pode fazer o que precisa.
--
-- Pense assim: o banco de dados é um ARMÁRIO GIGANTE.
-- A tabela "clientes" é uma GAVETA dentro do armário.
-- Cada cliente é uma FICHINHA dentro da gaveta.
-- =========================================================

-- 1) Cria o banco de dados (o "armário")
-- Rode este comando conectado como o usuário admin do Postgres (ex: postgres)
CREATE DATABASE loja_roupas;

-- Depois de criar, conecte-se a ele:
-- \c loja_roupas   (se estiver usando psql)

-- 2) Cria a tabela de clientes (a "gaveta")
CREATE TABLE IF NOT EXISTS clientes (
    id              SERIAL PRIMARY KEY,               -- número único, a "etiqueta" da fichinha
    nome            VARCHAR(100) NOT NULL,             -- nome do cliente
    email           VARCHAR(150) NOT NULL UNIQUE,      -- e-mail, não pode repetir
    telefone        VARCHAR(20),
    data_nascimento DATE,
    endereco        TEXT,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()   -- quando a fichinha foi criada
);

-- Índice para buscas rápidas por e-mail (muito comum no dia a dia)
CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes (email);

-- =========================================================
-- 3) SEGURANÇA: criar um usuário "de trabalho" que NÃO é o
-- super usuário (postgres). Isso é como dar uma CHAVEZINHA
-- que só abre a gaveta de clientes, e não o armário inteiro.
-- =========================================================

-- Cria o "papel" (role) que a aplicação vai usar para se conectar
CREATE ROLE app_loja WITH LOGIN PASSWORD 'LOGIN123';

-- Dá permissão só para USAR o banco (não para criar/apagar outros bancos)
GRANT CONNECT ON DATABASE loja_roupas TO app_loja;

-- Dá permissão só para mexer na tabela clientes (ler, inserir, alterar, apagar)
GRANT SELECT, INSERT, UPDATE, DELETE ON clientes TO app_loja;

-- Dá permissão de usar a sequência do id (necessário para o SERIAL funcionar)
GRANT USAGE, SELECT ON SEQUENCE clientes_id_seq TO app_loja;

-- IMPORTANTE: nunca use o usuário "postgres" (o super usuário) na aplicação.
-- Ele pode fazer QUALQUER coisa, inclusive apagar tudo sem querer.
