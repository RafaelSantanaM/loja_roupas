"""
app/core/logger.py
===================
Configuração de Logging Estruturado da aplicação.
Suporta Correlation ID (Request ID) via contextvars para rastreabilidade ponta a ponta.
"""

import logging
import sys
from contextvars import ContextVar

# Variável de contexto assíncrona para armazenar o ID único de cada requisição HTTP
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Filtro de logging que injeta o request_id atual do contexto em cada registro de log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


def setup_logger(name: str = "app") -> logging.Logger:
    """Configura e retorna uma instância padronizada de logger estruturado."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita duplicação de handlers se já configurado
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [req_id=%(request_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(RequestIdFilter())
        logger.addHandler(handler)

    return logger


# Instância padrão de logger da aplicação
logger = setup_logger("app")
