"""
app/routers/health_router.py
=============================
Endpoint de Health Check ativo para observabilidade e sondas de orquestração (Kubernetes, AWS, Cloud Run).
Testa a conectividade real com PostgreSQL, Redis e RabbitMQ.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
import pika

from app.core import cache
from app.core.config import settings
from app.core.logger import logger
from app.db.session import get_connection
from app.limiter import limiter

router = APIRouter(tags=["Observabilidade"])


@router.get("/health")
@limiter.limit("30/minute")
def health_check(request: Request):
    """
    Verifica a saúde ativa das três dependências fundamentais da infraestrutura:
    1. PostgreSQL (banco relacional)
    2. Redis (cache em memória)
    3. RabbitMQ (message broker)

    Retorna HTTP 200 (healthy) se todas estiverem ativas, ou HTTP 503 (unhealthy) se houver falha.
    """
    servicos = {}
    todos_saudaveis = True

    # 1. Checagem PostgreSQL
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            servicos["postgres"] = "ok"
        finally:
            conn.close()
    except Exception as erro:
        logger.error(f"Health Check: Falha de conexão com PostgreSQL: {erro}")
        servicos["postgres"] = f"erro: {erro}"
        todos_saudaveis = False

    # 2. Checagem Redis
    try:
        cache.r.ping()
        servicos["redis"] = "ok"
    except Exception as erro:
        logger.error(f"Health Check: Falha de conexão com Redis: {erro}")
        servicos["redis"] = f"erro: {erro}"
        todos_saudaveis = False

    # 3. Checagem RabbitMQ
    try:
        conexao = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                socket_timeout=3,
                blocked_connection_timeout=3,
            )
        )
        conexao.close()
        servicos["rabbitmq"] = "ok"
    except Exception as erro:
        logger.error(f"Health Check: Falha de conexão com RabbitMQ: {erro}")
        servicos["rabbitmq"] = f"erro: {erro}"
        todos_saudaveis = False

    conteudo = {
        "status": "healthy" if todos_saudaveis else "unhealthy",
        "servicos": servicos,
        "instancia": settings.instance_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if todos_saudaveis:
        return JSONResponse(status_code=status.HTTP_200_OK, content=conteudo)
    else:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=conteudo)
