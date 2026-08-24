"""
refresh_tokens_crud.py
=======================
Gerencia os refresh tokens guardados no banco -- permite revogar um
token antes da hora dele expirar sozinho.
"""

from app.db.session import get_connection


def salvar_refresh_token(usuario_id: int, jti: str, expira_em) -> None:
    sql = "INSERT INTO refresh_tokens (usuario_id, jti, expira_em) VALUES (%s, %s, %s);"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (usuario_id, jti, expira_em))
            conn.commit()


def refresh_token_esta_ativo(jti: str) -> bool:
    sql = """
        SELECT 1 FROM refresh_tokens
        WHERE jti = %s AND revogado = FALSE AND expira_em > NOW();
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (jti,))
            return cursor.fetchone() is not None


def revogar_refresh_token(jti: str) -> None:
    sql = "UPDATE refresh_tokens SET revogado = TRUE WHERE jti = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (jti,))
            conn.commit()
