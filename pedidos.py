"""
pedidos.py
==========
Exercício de TRANSAÇÃO de verdade: criar um pedido precisa fazer
DUAS coisas ao mesmo tempo:
  1) Diminuir o estoque do produto
  2) Registrar o pedido

Se o estoque não for suficiente, NADA deve ser salvo — nem o
pedido, nem qualquer alteração no estoque. É "tudo ou nada".

Aqui, diferente do crud.py, fazemos o commit/rollback de forma
BEM explícita (com try/except), só pra você ver o mecanismo
acontecendo na prática.
"""

from db import get_connection


class EstoqueInsuficiente(Exception):
    """Erro criado por nós mesmos, pra avisar que não tem produto suficiente."""
    pass


def criar_pedido(cliente_id, produto_id, quantidade):
    """
    Cria um pedido de forma transacional.

    Passo a passo do que acontece:
    1. Abre a conexão e DESLIGA o "modo automático" de commit
       (autocommit=False é o padrão do psycopg2, então já começamos
       dentro de uma transação assim que conectamos).
    2. Tenta diminuir o estoque e inserir o pedido.
    3. Se der tudo certo -> conn.commit() (confirma tudo de vez).
    4. Se algo der errado -> conn.rollback() (desfaz tudo, como se
       nada tivesse acontecido).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1) Verifica o preço e o estoque atual do produto
            cursor.execute(
                "SELECT preco, estoque FROM produtos WHERE id = %s FOR UPDATE;",
                (produto_id,),
            )
            resultado = cursor.fetchone()
            if resultado is None:
                raise ValueError("Produto não encontrado.")

            preco, estoque_atual = resultado

            # 2) Regra de negócio: não deixa pedir mais do que tem em estoque
            if quantidade > estoque_atual:
                raise EstoqueInsuficiente(
                    f"Só temos {estoque_atual} unidade(s) em estoque, "
                    f"mas foram pedidas {quantidade}."
                )

            # 3) Diminui o estoque
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - %s WHERE id = %s;",
                (quantidade, produto_id),
            )

            # 4) Registra o pedido
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

        # Se chegou até aqui, tudo deu certo -> CONFIRMA de vez
        conn.commit()
        print(f"✅ Pedido {pedido_id} criado com sucesso! Total: R$ {valor_total}")
        return pedido_id

    except Exception as erro:
        # Algo deu errado em QUALQUER ponto acima -> DESFAZ TUDO
        conn.rollback()
        print(f"❌ Pedido cancelado, nada foi salvo. Motivo: {erro}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    # --- Cenário 1: pedido válido (dentro do estoque) ---
    print("Tentando um pedido válido (1 camiseta)...")
    try:
        criar_pedido(cliente_id=1, produto_id=1, quantidade=1)
    except Exception:
        pass

    print()

    # --- Cenário 2: pedido inválido (mais do que tem em estoque) ---
    # Isso força o ROLLBACK, pra você ver o "desfazer tudo" na prática.
    print("Tentando um pedido inválido (100 camisetas, sem estoque suficiente)...")
    try:
        criar_pedido(cliente_id=1, produto_id=1, quantidade=100)
    except EstoqueInsuficiente:
        pass
