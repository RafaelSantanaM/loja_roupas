"""
db.py
=====
Aqui é o "porteiro" do banco de dados: só ele sabe o caminho até o
banco e como bater na porta certinho.

Antes deste commit, este arquivo lia a configuração sozinho, com
os.getenv() e load_dotenv() manual. Agora ele importa a configuração
JÁ PRONTA de app/core/config.py -- não muda o QUE ele faz, só de
ONDE ele busca os valores.
"""

import psycopg2

from app.core.config import settings


def get_connection():
    """
    Abre uma conexão segura com o PostgreSQL, usando a configuração
    centralizada.
    """
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
