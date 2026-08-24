"""
app/core/config.py
====================
Configuração CENTRALIZADA da aplicação. Antes deste commit, cada
arquivo lia configuração à sua própria maneira:
  - db.py usava os.getenv() com load_dotenv() manual
  - auth.py usava os.getenv() só para o segredo do JWT, e tinha
    ALGORITMO/MINUTOS_ACCESS_TOKEN/DIAS_REFRESH_TOKEN fixos no código
  - cache.py e filas.py tinham host/porta escritos DIRETO no código,
    sem nem passar por variável de ambiente
  - app/main.py usava os.getenv() só para o INSTANCE_NAME

Isso é frágil: não existe um único lugar para conferir "tudo que este
sistema precisa para rodar", e um valor mudado num arquivo não se
reflete automaticamente em outro que dependa do mesmo dado.

Com pydantic-settings, TODA configuração vira um campo tipado nesta
classe. A biblioteca lê variáveis de ambiente (ou um arquivo .env)
automaticamente, convertendo o texto para o tipo certo (int, str...),
e gera um erro claro na inicialização se algo obrigatório faltar --
em vez de descobrir isso só quando o código tentar usar o valor,
no meio de uma requisição.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Banco de dados (antes em db.py) ---
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "loja_roupas"
    db_user: str = "app_loja"
    db_password: str = ""
    db_sslmode: str = "prefer"

    # --- Autenticação (antes em auth.py) ---
    jwt_secret_key: str = "troque-essa-chave-em-producao"
    jwt_algoritmo: str = "HS256"
    minutos_access_token: int = 15
    dias_refresh_token: int = 7

    # --- Cache / Redis (antes hardcoded em cache.py) ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    cache_ttl_segundos: int = 60

    # --- Fila / RabbitMQ (antes hardcoded em filas.py) ---
    rabbitmq_host: str = "localhost"

    # --- CORS (antes hardcoded em app/main.py) ---
    origens_permitidas: list[str] = ["http://127.0.0.1:5500", "http://localhost:5500"]

    # --- Identificação da instância (antes em app/main.py via os.getenv) ---
    instance_name: str = "instancia-desconhecida"

    # Lê automaticamente um arquivo .env na raiz do projeto, além de
    # variáveis de ambiente reais do sistema operacional.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instância única (padrão "Singleton"), importada por todo o resto do
# projeto. Só existe UM objeto de configuração vivo durante a execução
# inteira, evitando reler o .env repetidamente ou ter valores
# divergentes em partes diferentes do código.
settings = Settings()
