"""
crud.py
=======
Aqui estão as 4 ações mágicas que dá pra fazer com uma fichinha de cliente:

  C - Criar    (adicionar uma fichinha nova na gaveta)
  R - Ler      (olhar as fichinhas que já existem)
  U - Atualizar (mudar alguma informação de uma fichinha)
  D - Deletar  (jogar fora uma fichinha)

REGRA DE OURO DE SEGURANÇA:
Nunca, jamais, monte a "pergunta" (query) colando o texto do usuário
direto nela, tipo: f"SELECT * FROM clientes WHERE nome = '{nome}'"
Isso se chama SQL Injection e é uma das formas mais fáceis de
alguém "invadir" um banco de dados.

O jeito seguro é usar "%s" como um espaço reservado, e passar os
valores separados. O próprio psycopg2 cuida de "limpar" o valor
para ele não conseguir fazer travessuras.
"""

from db import get_connection


def criar_cliente(nome, email, telefone=None, data_nascimento=None, endereco=None):
    """Adiciona um cliente novo na gaveta."""
    sql = """
        INSERT INTO clientes (nome, email, telefone, data_nascimento, endereco)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, email, telefone, data_nascimento, endereco))
            novo_id = cursor.fetchone()[0]
            conn.commit()
    return novo_id


def listar_clientes(limite=10, offset=0, nome=None):
    """
    Mostra as fichinhas da gaveta, com PAGINAÇÃO e filtro opcional por nome.

    limite -> quantos clientes trazer por "página" (padrão 10)
    offset -> quantos pular antes de começar a contar (padrão 0, ou seja, do início)
    nome   -> se informado, só traz clientes cujo nome contenha esse texto
    """
    sql = """
        SELECT id, nome, email, telefone, data_nascimento, endereco, criado_em
        FROM clientes
        WHERE (%(nome)s IS NULL OR nome ILIKE '%%' || %(nome)s || '%%')
        ORDER BY id
        LIMIT %(limite)s OFFSET %(offset)s;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"nome": nome, "limite": limite, "offset": offset})
            return cursor.fetchall()


def contar_clientes(nome=None):
    """Conta quantos clientes existem no total (útil para calcular o número de páginas)."""
    sql = "SELECT COUNT(*) FROM clientes WHERE (%(nome)s IS NULL OR nome ILIKE '%%' || %(nome)s || '%%');"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"nome": nome})
            return cursor.fetchone()[0]


def buscar_cliente_por_id(cliente_id):
    """Procura UMA fichinha específica pelo número dela (id)."""
    sql = "SELECT id, nome, email, telefone, data_nascimento, endereco, criado_em FROM clientes WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (cliente_id,))
            return cursor.fetchone()


def atualizar_cliente(cliente_id, nome=None, telefone=None, endereco=None):
    """Muda alguma informação de um cliente que já existe."""
    sql = """
        UPDATE clientes
        SET nome = COALESCE(%s, nome),
            telefone = COALESCE(%s, telefone),
            endereco = COALESCE(%s, endereco)
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, telefone, endereco, cliente_id))
            linhas_alteradas = cursor.rowcount
            conn.commit()
    return linhas_alteradas


def deletar_cliente(cliente_id):
    """Joga fora a fichinha de um cliente."""
    sql = "DELETE FROM clientes WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (cliente_id,))
            linhas_apagadas = cursor.rowcount
            conn.commit()
    return linhas_apagadas
