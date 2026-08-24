"""
app/db/session.py
===================
O "porteiro" da conexão com o PostgreSQL.

Antes deste commit, este arquivo era db.py, solto na raiz do
projeto. Movido para app/db/ -- essa pasta vai conter, além disso,
as migrations SQL (num commit futuro), reunindo tudo que é "camada
de banco de dados" num único lugar reconhecível.

O CONTEÚDO não mudou -- só o endereço.
"""

import psycopg2

from app.core.config import settings


def get_connection():
    """Abre uma conexão segura com o PostgreSQL, usando a configuração centralizada."""
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        sslmode=settings.db_sslmode,
        connect_timeout=5,
    )


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conectou certinho no banco de dados!")
        conn.close()
    except Exception as erro:
        print("❌ Não consegui conectar. Erro:", erro)
