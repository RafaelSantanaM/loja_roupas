"""
app/repositories/usuario_repo.py
==================================
Repositório de acesso a dados da entidade Usuário (autenticação e RBAC).
"""

from typing import Optional, Any
from app.db.session import get_connection
from app.core.security import gerar_hash_senha


def criar_usuario(username: str, senha_pura: str, papel: str = "funcionario") -> int:
    """Cria um novo usuário salvando a senha já protegida por hash bcrypt."""
    senha_hash = gerar_hash_senha(senha_pura)
    sql = "INSERT INTO usuarios (username, senha_hash, papel) VALUES (%s, %s, %s) RETURNING id;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (username, senha_hash, papel))
            novo_id = cursor.fetchone()[0]
            conn.commit()
    return novo_id


def buscar_usuario_por_username(username: str) -> Optional[tuple[Any, ...]]:
    """Devolve a tupla (id, username, senha_hash, papel) ou None se não encontrado."""
    sql = "SELECT id, username, senha_hash, papel FROM usuarios WHERE username = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (username,))
            return cursor.fetchone()
