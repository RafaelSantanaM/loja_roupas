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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.limiter import limiter
from app.routers import auth_router, clientes_router

app = FastAPI(title="API - Cadastro de Clientes")

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
app.include_router(auth_router.router)
app.include_router(clientes_router.router)


@app.get("/")
def raiz():
    """Rota simples para conferir se a API está no ar, e qual instância atendeu."""
    return {
        "mensagem": "API da loja de roupas está funcionando!",
        "atendido_por": settings.instance_name,
    }
