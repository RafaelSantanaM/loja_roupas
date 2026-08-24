"""
usuarios_crud.py
================
CRUD simples para a tabela de usuários (quem pode logar na API).
"""

from app.db.session import get_connection
from app.core.security import gerar_hash_senha


def criar_usuario(username: str, senha_pura: str, papel: str = "funcionario") -> int:
    senha_hash = gerar_hash_senha(senha_pura)
    sql = "INSERT INTO usuarios (username, senha_hash, papel) VALUES (%s, %s, %s) RETURNING id;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (username, senha_hash, papel))
            novo_id = cursor.fetchone()[0]
            conn.commit()
    return novo_id


def buscar_usuario_por_username(username: str):
    """Devolve (id, username, senha_hash, papel) ou None se não existir."""
    sql = "SELECT id, username, senha_hash, papel FROM usuarios WHERE username = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (username,))
            return cursor.fetchone()


if __name__ == "__main__":
    novo_id = criar_usuario("gerente", "senha123", papel="admin")
    print(f"Usuário 'gerente' (admin) criado com id={novo_id}.")

    novo_id = criar_usuario("vendedor", "senha123", papel="funcionario")
    print(f"Usuário 'vendedor' (funcionario) criado com id={novo_id}.")
