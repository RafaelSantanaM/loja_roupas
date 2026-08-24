"""
crud.py
=======
Aqui estão as 4 ações mágicas que dá pra fazer com uma fichinha de cliente:
  C - Criar, R - Ler, U - Atualizar, D - Deletar

REGRA DE OURO DE SEGURANÇA: sempre parametrizado (%s), nunca montando
SQL colando texto do usuário direto (SQL Injection).
"""

from app.db.session import get_connection


def criar_cliente(nome, email, telefone=None, data_nascimento=None, endereco=None):
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
    sql = "SELECT COUNT(*) FROM clientes WHERE (%(nome)s IS NULL OR nome ILIKE '%%' || %(nome)s || '%%');"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"nome": nome})
            return cursor.fetchone()[0]


def buscar_cliente_por_id(cliente_id):
    sql = "SELECT id, nome, email, telefone, data_nascimento, endereco, criado_em FROM clientes WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (cliente_id,))
            return cursor.fetchone()


def atualizar_cliente(cliente_id, nome=None, telefone=None, endereco=None):
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
    sql = "DELETE FROM clientes WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (cliente_id,))
            linhas_apagadas = cursor.rowcount
            conn.commit()
    return linhas_apagadas
