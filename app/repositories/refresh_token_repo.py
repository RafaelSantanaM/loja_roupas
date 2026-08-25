"""
app/repositories/refresh_token_repo.py
========================================
Repositório de acesso a dados para controle de ciclo de vida de Refresh Tokens.
Permite o armazenamento de identificadores de token (jti), verificação de validade e revogação ativa.
"""

from datetime import datetime
from app.db.session import get_connection


def salvar_refresh_token(usuario_id: int, jti: str, expira_em: datetime) -> None:
    """Registra um novo refresh token associado a um usuário."""
    sql = "INSERT INTO refresh_tokens (usuario_id, jti, expira_em) VALUES (%s, %s, %s);"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (usuario_id, jti, expira_em))
            conn.commit()


def refresh_token_esta_ativo(jti: str) -> bool:
    """Verifica se o token existe, não foi revogado e ainda está dentro do prazo de expiração."""
    sql = """
        SELECT 1 FROM refresh_tokens
        WHERE jti = %s AND revogado = FALSE AND expira_em > NOW();
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (jti,))
            return cursor.fetchone() is not None


def revogar_refresh_token(jti: str) -> None:
    """Marca um refresh token como revogado (usado no logout)."""
    sql = "UPDATE refresh_tokens SET revogado = TRUE WHERE jti = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (jti,))
            conn.commit()
