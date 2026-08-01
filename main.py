"""
main.py
=======
Script de demonstração. Rode este arquivo para ver o cadastro
de clientes funcionando na prática, passo a passo.
"""

from crud import (
    criar_cliente,
    listar_clientes,
    buscar_cliente_por_id,
    atualizar_cliente,
    deletar_cliente,
)


def main():
    print("1) Criando um cliente novo...")
    novo_id = criar_cliente(
        nome="Maria Silva",
        email="maria.silva@example.com",
        telefone="11999998888",
        data_nascimento="1995-04-12",
        endereco="Rua das Flores, 123",
    )
    print(f"   Cliente criado com id = {novo_id}\n")

    print("2) Listando todos os clientes...")
    for cliente in listar_clientes():
        print("  ", cliente)
    print()

    print(f"3) Buscando o cliente {novo_id}...")
    print("  ", buscar_cliente_por_id(novo_id), "\n")

    print(f"4) Atualizando o telefone do cliente {novo_id}...")
    atualizar_cliente(novo_id, telefone="11888887777")
    print("  ", buscar_cliente_por_id(novo_id), "\n")

    print(f"5) Apagando o cliente {novo_id}...")
    deletar_cliente(novo_id)
    print("   Cliente apagado!\n")


if __name__ == "__main__":
    main()
