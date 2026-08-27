"""
app/repositories/pedido_repo.py
=================================
Repositório de acesso a dados da entidade Pedidos.
Executa transações bancárias estritas (ACID) com controle de concorrência pessimista (SELECT FOR UPDATE).
"""

from typing import Optional, Any
from app.db.session import get_connection


class EstoqueInsuficienteError(Exception):
    """Exceção levantada quando a quantidade pedida supera o estoque disponível."""
    pass


class ProdutoNaoEncontradoError(Exception):
    """Exceção levantada quando o produto especificado no pedido não existe."""
    pass


class ClienteNaoEncontradoError(Exception):
    """Exceção levantada quando o cliente especificado não existe."""
    pass


def criar_pedido(
    cliente_id: int,
    produto_id: int,
    quantidade: int,
) -> tuple[int, float, str, str, str]:
    """
    Executa a criação atômica de pedido:
    1. Valida a existência do cliente.
    2. Bloqueia a linha do produto no PostgreSQL (SELECT FOR UPDATE) para evitar race condition.
    3. Valida se o estoque é suficiente.
    4. Realiza o débito no estoque e insere o registro do pedido.
    5. Efetua o commit atômico ou rollback em caso de falha.

    Retorna: (pedido_id, valor_total, nome_produto, nome_cliente, email_cliente)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Verifica existência do cliente
            cursor.execute("SELECT nome, email FROM clientes WHERE id = %s;", (cliente_id,))
            cliente = cursor.fetchone()
            if cliente is None:
                raise ClienteNaoEncontradoError(f"Cliente com ID {cliente_id} não existe.")
            nome_cliente, email_cliente = cliente

            # 2. Trava pessimista na linha do produto (SELECT ... FOR UPDATE)
            cursor.execute(
                "SELECT nome, preco, estoque FROM produtos WHERE id = %s FOR UPDATE;",
                (produto_id,),
            )
            produto = cursor.fetchone()
            if produto is None:
                raise ProdutoNaoEncontradoError(f"Produto com ID {produto_id} não existe.")
            nome_produto, preco, estoque_atual = produto

            # 3. Validação de integridade de estoque
            if quantidade > estoque_atual:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente. Disponível: {estoque_atual}, solicitado: {quantidade}."
                )

            # 4. Baixa atômica de estoque
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - %s WHERE id = %s;",
                (quantidade, produto_id),
            )

            # 5. Criação do pedido
            valor_total = float(preco) * quantidade
            cursor.execute(
                """
                INSERT INTO pedidos (cliente_id, produto_id, quantidade, valor_total)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (cliente_id, produto_id, quantidade, valor_total),
            )
            pedido_id = cursor.fetchone()[0]

        conn.commit()
        return pedido_id, valor_total, nome_produto, nome_cliente, email_cliente

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def listar_pedidos(
    limite: int = 10,
    offset: int = 0,
    cliente_id: Optional[int] = None,
) -> list[tuple[Any, ...]]:
    """Lista histórico de pedidos com paginação e filtro opcional por cliente."""
    sql = """
        SELECT id, cliente_id, produto_id, quantidade, valor_total, criado_em
        FROM pedidos
        WHERE (%(cliente_id)s IS NULL OR cliente_id = %(cliente_id)s)
        ORDER BY id DESC
        LIMIT %(limite)s OFFSET %(offset)s;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"cliente_id": cliente_id, "limite": limite, "offset": offset})
            return cursor.fetchall()


def contar_pedidos(cliente_id: Optional[int] = None) -> int:
    """Retorna o total de pedidos cadastrados, com filtro opcional por cliente."""
    sql = "SELECT COUNT(*) FROM pedidos WHERE (%(cliente_id)s IS NULL OR cliente_id = %(cliente_id)s);"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"cliente_id": cliente_id})
            return cursor.fetchone()[0]


def buscar_pedido_por_id(pedido_id: int) -> Optional[tuple[Any, ...]]:
    """Busca os detalhes de um pedido específico por ID."""
    sql = """
        SELECT id, cliente_id, produto_id, quantidade, valor_total, criado_em
        FROM pedidos
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (pedido_id,))
            return cursor.fetchone()
