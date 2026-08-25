"""
app/repositories/cliente_repo.py
==================================
Repositório de acesso a dados da entidade Cliente.
Executa operações de persistência (CRUD) diretamente no PostgreSQL.

Segurança: Todas as consultas utilizam consultas parametrizadas (%s ou %(nome)s)
para prevenir vulnerabilidades de SQL Injection.
"""

from typing import Optional, Any
from app.db.session import get_connection


def criar_cliente(
    nome: str,
    email: str,
    telefone: Optional[str] = None,
    data_nascimento: Optional[str] = None,
    endereco: Optional[str] = None,
) -> int:
    """Insere um novo cliente no banco e retorna seu ID gerado."""
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


def listar_clientes(
    limite: int = 10,
    offset: int = 0,
    nome: Optional[str] = None,
) -> list[tuple[Any, ...]]:
    """Lista clientes com suporte a paginação e filtro opcional por nome."""
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


def contar_clientes(nome: Optional[str] = None) -> int:
    """Retorna o total de clientes cadastrados, com filtro opcional por nome."""
    sql = "SELECT COUNT(*) FROM clientes WHERE (%(nome)s IS NULL OR nome ILIKE '%%' || %(nome)s || '%%');"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"nome": nome})
            return cursor.fetchone()[0]


def buscar_cliente_por_id(cliente_id: int) -> Optional[tuple[Any, ...]]:
    """Busca um cliente específico por seu ID único."""
    sql = "SELECT id, nome, email, telefone, data_nascimento, endereco, criado_em FROM clientes WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (cliente_id,))
            return cursor.fetchone()


def atualizar_cliente(
    cliente_id: int,
    nome: Optional[str] = None,
    telefone: Optional[str] = None,
    endereco: Optional[str] = None,
) -> int:
    """Atualiza campos específicos de um cliente. Retorna o número de linhas afetadas."""
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


def deletar_cliente(cliente_id: int) -> int:
    """Remove um cliente pelo ID. Retorna o número de linhas afetadas."""
    sql = "DELETE FROM clientes WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (cliente_id,))
            linhas_apagadas = cursor.rowcount
            conn.commit()
    return linhas_apagadas
