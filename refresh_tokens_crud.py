"""
refresh_tokens_crud.py
=======================
Gerencia os refresh tokens guardados no banco. É essa "lembrança"
no banco que permite REVOGAR um token antes da hora dele expirar
sozinho -- algo que um JWT, por si só, nunca permite fazer.
"""

from db import get_connection


def salvar_refresh_token(usuario_id: int, jti: str, expira_em) -> None:
    """Registra um refresh token novo como 'ativo'."""
    sql = "INSERT INTO refresh_tokens (usuario_id, jti, expira_em) VALUES (%s, %s, %s);"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (usuario_id, jti, expira_em))
            conn.commit()


def refresh_token_esta_ativo(jti: str) -> bool:
    """
    Confere se esse jti existe no banco, NÃO foi revogado, e ainda
    não passou da data de expiração guardada.
    """
    sql = """
        SELECT 1 FROM refresh_tokens
        WHERE jti = %s AND revogado = FALSE AND expira_em > NOW();
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (jti,))
            return cursor.fetchone() is not None


def revogar_refresh_token(jti: str) -> None:
    """'Cancela' um refresh token antes da hora -- usado no logout."""
    sql = "UPDATE refresh_tokens SET revogado = TRUE WHERE jti = %s;"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (jti,))
            conn.commit()
