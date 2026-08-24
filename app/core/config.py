"""
app/core/config.py
====================
Configuração CENTRALIZADA da aplicação.

SEGURANÇA: jwt_secret_key e db_password NÃO têm valor padrão. Isso é
proposital -- são segredos, e um segredo com "valor de exemplo"
embutido no código-fonte público é uma vulnerabilidade conhecida,
catalogada como "insecure default" (CWE-1188) e relacionada a
"hard-coded credentials" (CWE-798).

Sem valor padrão, o pydantic-settings FALHA NA INICIALIZAÇÃO se essas
variáveis não estiverem definidas no .env ou no ambiente -- a
aplicação recusa-se a subir "silenciosamente insegura". É melhor
travar na hora do deploy, com um erro claro, do que rodar em produção
usando um segredo que qualquer pessoa lendo o repositório já conhece.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Banco de dados ---
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "loja_roupas"
    db_user: str = "app_loja"
    db_password: str          # OBRIGATÓRIO -- sem valor padrão, de propósito
    db_sslmode: str = "prefer"

    # --- Autenticação ---
    jwt_secret_key: str       # OBRIGATÓRIO -- sem valor padrão, de propósito
    jwt_algoritmo: str = "HS256"
    minutos_access_token: int = 15
    dias_refresh_token: int = 7

    # --- Cache / Redis ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    cache_ttl_segundos: int = 60

    # --- Fila / RabbitMQ ---
    rabbitmq_host: str = "localhost"

    # --- CORS ---
    origens_permitidas: list[str] = ["http://127.0.0.1:5500", "http://localhost:5500"]

    # --- Identificação da instância ---
    instance_name: str = "instancia-desconhecida"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
