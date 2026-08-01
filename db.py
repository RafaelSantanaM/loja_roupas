"""
db.py
=====
Este arquivo é o "porteiro" do prédio: ele é o único que sabe
o caminho até o banco de dados e como bater na porta certinho.

Por que fazer assim?
- A senha NUNCA fica escrita direto no código (fica no .env).
- Só existe UM lugar que abre conexão, então é mais fácil de proteger.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para dentro do programa
load_dotenv()


def get_connection():
    """
    Abre uma conexão segura com o PostgreSQL.

    Pense nisso como discar um telefone:
    - DB_HOST + DB_PORT = o número de telefone da casa do banco de dados
    - DB_NAME           = o cômodo da casa que queremos entrar
    - DB_USER/PASSWORD  = a senha para a pessoa te deixar entrar
    - sslmode           = pedir para conversar "em código secreto" (criptografado)
    """
    conexao = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "loja_roupas"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
        connect_timeout=5,  # não fica esperando pra sempre se algo der errado
    )
    return conexao


if __name__ == "__main__":
    # Teste rápido: só tenta ligar e avisa se deu certo
    try:
        conn = get_connection()
        print("✅ Conectou certinho no banco de dados!")
        conn.close()
    except Exception as erro:
        print("❌ Não consegui conectar. Erro:", erro)
