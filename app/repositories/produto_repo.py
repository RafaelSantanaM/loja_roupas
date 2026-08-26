"""
app/repositories/produto_repo.py
==================================
Repositório de acesso a dados da entidade Produto (catálogo e estoque de roupas).
Executa operações de persistência com SQL parametrizado contra o PostgreSQL.
"""

from typing import Optional, Any
from app.db.session import get_connection


def criar_produto(nome: str, preco: float, estoque: int = 0) -> int:
    """Cadastra um novo produto no banco de dados e retorna seu ID gerado."""
    sql = """
        INSERT INTO produtos (nome, preco, estoque)
        VALUES (%s, %s, %s)
        RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, preco, estoque))
            novo_id = cursor.fetchone()[0]
            conn.commit()
    return novo_id


def listar_produtos(
    limite: int = 10,
    offset: int = 0,
    nome: Optional[str] = None,
) -> list[tuple[Any, ...]]:
    """Lista produtos cadastrados com paginação e filtro opcional por nome."""
    sql = """
        SELECT id, nome, preco, estoque
        FROM produtos
        WHERE (%(nome)s IS NULL OR nome ILIKE '%%' || %(nome)s || '%%')
        ORDER BY id
        LIMIT %(limite)s OFFSET %(offset)s;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"nome": nome, "limite": limite, "offset": offset})
            return cursor.fetchall()


def contar_produtos(nome: Optional[str] = None) -> int:
    """Retorna o total de produtos cadastrados, com filtro opcional por nome."""
    sql = "SELECT COUNT(*) FROM produtos WHERE (%(nome)s IS NULL OR nome ILIKE '%%' || %(nome)s || '%%');"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"nome": nome})
            return cursor.fetchone()[0]


def buscar_produto_por_id(produto_id: int) -> Optional[tuple[Any, ...]]:
    """Busca um produto específico pelo seu ID."""
    sql = "SELECT id, nome, preco, estoque FROM produtos WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (produto_id,))
            return cursor.fetchone()


def atualizar_produto(
    produto_id: int,
    nome: Optional[str] = None,
    preco: Optional[float] = None,
    estoque: Optional[int] = None,
) -> int:
    """Atualiza dados do produto (nome, preço ou quantidade em estoque). Retorna linhas afetadas."""
    sql = """
        UPDATE produtos
        SET nome = COALESCE(%s, nome),
            preco = COALESCE(%s, preco),
            estoque = COALESCE(%s, estoque)
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, preco, estoque, produto_id))
            linhas_alteradas = cursor.rowcount
            conn.commit()
    return linhas_alteradas


def deletar_produto(produto_id: int) -> int:
    """Remove um produto do catálogo. Retorna o número de linhas apagadas."""
    sql = "DELETE FROM produtos WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (produto_id,))
            linhas_apagadas = cursor.rowcount
            conn.commit()
    return linhas_apagadas
