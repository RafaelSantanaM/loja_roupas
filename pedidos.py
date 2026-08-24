"""
pedidos.py
==========
Exercício de TRANSAÇÃO de verdade: criar um pedido precisa fazer
DUAS coisas ao mesmo tempo:
  1) Diminuir o estoque do produto
  2) Registrar o pedido

Se o estoque não for suficiente, NADA deve ser salvo -- nem o
pedido, nem qualquer alteração no estoque. É "tudo ou nada".

Aqui, diferente do crud.py, fazemos o commit/rollback de forma
BEM explícita (com try/except), só pra você ver o mecanismo
acontecendo na prática.
"""

from app.db.session import get_connection


class EstoqueInsuficiente(Exception):
    """Erro criado por nós mesmos, pra avisar que não tem produto suficiente."""
    pass


def criar_pedido(cliente_id, produto_id, quantidade):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT preco, estoque FROM produtos WHERE id = %s FOR UPDATE;",
                (produto_id,),
            )
            resultado = cursor.fetchone()
            if resultado is None:
                raise ValueError("Produto não encontrado.")

            preco, estoque_atual = resultado

            if quantidade > estoque_atual:
                raise EstoqueInsuficiente(
                    f"Só temos {estoque_atual} unidade(s) em estoque, "
                    f"mas foram pedidas {quantidade}."
                )

            cursor.execute(
                "UPDATE produtos SET estoque = estoque - %s WHERE id = %s;",
                (quantidade, produto_id),
            )

            valor_total = preco * quantidade
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
        print(f"✅ Pedido {pedido_id} criado com sucesso! Total: R$ {valor_total}")
        return pedido_id

    except Exception as erro:
        conn.rollback()
        print(f"❌ Pedido cancelado, nada foi salvo. Motivo: {erro}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    print("Tentando um pedido válido (1 camiseta)...")
    try:
        criar_pedido(cliente_id=1, produto_id=1, quantidade=1)
    except Exception:
        pass

    print()

    print("Tentando um pedido inválido (100 camisetas, sem estoque suficiente)...")
    try:
        criar_pedido(cliente_id=1, produto_id=1, quantidade=100)
    except EstoqueInsuficiente:
        pass
