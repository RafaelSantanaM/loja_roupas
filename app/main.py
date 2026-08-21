"""
app/main.py
=============
Substitui o antigo api.py. Repare a diferença de tamanho: o que eram
~340 linhas fazendo tudo junto virou ~35 linhas que só "montam" as
peças já construídas nos outros arquivos -- middlewares, e os dois
routers.

Como rodar (a partir da raiz do projeto, igual sempre foi):
    uvicorn app.main:app --reload

NOTA: CORS, rate limiting e a variável INSTANCE_NAME continuam
exatamente como estavam no api.py original (valores fixos no código,
via os.getenv) -- centralizar isso em app/core/config.py é uma
refatoração separada, ainda por vir.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.limiter import limiter
from app.routers import auth_router, clientes_router

app = FastAPI(title="API - Cadastro de Clientes")

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --- CORS ---
ORIGENS_PERMITIDAS = ["http://127.0.0.1:5500", "http://localhost:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth_router.router)
app.include_router(clientes_router.router)


@app.get("/")
def raiz():
    """Rota simples para conferir se a API está no ar."""
    instancia = os.getenv("INSTANCE_NAME", "instancia-desconhecida")
    return {"mensagem": "API da loja de roupas está funcionando!", "atendido_por": instancia}
