-- =========================================================
-- MIGRACAO_RBAC.SQL
-- Roda isso se você JÁ TEM a tabela "usuarios" criada
-- (ou seja, você já fez o exercício de autenticação antes).
--
-- Uma "migração" é assim: um scriptzinho que ajusta um banco
-- que já existe, em vez de criar tudo do zero de novo.
-- =========================================================

-- Adiciona a coluna, com um valor padrão pra quem já existe
ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS papel VARCHAR(20) NOT NULL DEFAULT 'funcionario';

-- Garante que só aceita esses dois valores dali pra frente
ALTER TABLE usuarios
    ADD CONSTRAINT usuarios_papel_check CHECK (papel IN ('admin', 'funcionario'));

-- Promove o usuário "admin" que você já criou para o papel de admin de verdade
UPDATE usuarios SET papel = 'admin' WHERE username = 'admin';
