"""
app/main.py
=============
Ponto de entrada da aplicação -- monta middlewares e routers.

Neste commit, INSTANCE_NAME e a lista de origens de CORS deixam de
vir de os.getenv()/valor fixo direto aqui, e passam a vir da
configuração centralizada.

Como rodar (a partir da raiz do projeto):
    uvicorn app.main:app --reload
"""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.logger import logger, request_id_ctx
from app.limiter import limiter
from app.routers import (
    auth_router,
    clientes_router,
    produtos_router,
    pedidos_router,
    health_router,
)

app = FastAPI(title="Loja de Roupas - Enterprise API")


# --- Middleware: Correlation ID & Logging Estruturado ---
@app.middleware("http")
async def correlation_id_and_logging_middleware(request: Request, call_next):
    # Obtém ou gera um correlation ID único para a requisição
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx.set(req_id)

    inicio = time.perf_counter()
    logger.info(f"--> {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        duracao_ms = (time.perf_counter() - inicio) * 1000
        logger.info(
            f"<-- {request.method} {request.url.path} - Status: {response.status_code} ({duracao_ms:.2f}ms)"
        )
        response.headers["X-Request-ID"] = req_id
        return response
    except Exception as exc:
        duracao_ms = (time.perf_counter() - inicio) * 1000
        logger.error(
            f"<-- {request.method} {request.url.path} - Exceção não tratada: {exc} ({duracao_ms:.2f}ms)",
            exc_info=True,
        )
        raise exc
    finally:
        request_id_ctx.reset(token)


# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origens_permitidas,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(clientes_router.router)
app.include_router(produtos_router.router)
app.include_router(pedidos_router.router)


@app.get("/")
def raiz():
    """Rota simples para conferir se a API está no ar, e qual instância atendeu."""
    return {
        "mensagem": "API da loja de roupas está funcionando!",
        "atendido_por": settings.instance_name,
    }
