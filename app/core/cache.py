"""
app/core/cache.py
===================
Camada de cache em memória utilizando Redis.
Implementa estratégias de Cache-Aside, serialização JSON, TTL (Time to Live) e invalidação ativa.
"""

import json
from typing import Optional, Any
import redis

from app.core.config import settings

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


# --- Domínio: Clientes ---

def chave_cliente(cliente_id: int) -> str:
    """Padroniza o formato da chave de cliente no Redis."""
    return f"cliente:{cliente_id}"


def buscar_cliente_no_cache(cliente_id: int) -> Optional[dict[str, Any]]:
    """Retorna o dicionário do cliente se estiver em cache, ou None (cache miss)."""
    valor = r.get(chave_cliente(cliente_id))
    if valor is None:
        return None
    return json.loads(valor)


def salvar_cliente_no_cache(cliente_id: int, dados: dict[str, Any]) -> None:
    """Grava o cliente no cache com tempo de expiração automático (TTL)."""
    r.set(chave_cliente(cliente_id), json.dumps(dados, default=str), ex=settings.cache_ttl_segundos)


def invalidar_cliente_no_cache(cliente_id: int) -> None:
    """Remove ativamente uma entrada de cliente no Redis (usado em UPDATE e DELETE)."""
    r.delete(chave_cliente(cliente_id))


# --- Domínio: Produtos ---

def chave_produto(produto_id: int) -> str:
    """Padroniza o formato da chave de produto no Redis."""
    return f"produto:{produto_id}"


def buscar_produto_no_cache(produto_id: int) -> Optional[dict[str, Any]]:
    """Retorna o dicionário do produto se estiver em cache, ou None (cache miss)."""
    valor = r.get(chave_produto(produto_id))
    if valor is None:
        return None
    return json.loads(valor)


def salvar_produto_no_cache(produto_id: int, dados: dict[str, Any]) -> None:
    """Grava o produto no cache com tempo de expiração automático (TTL)."""
    r.set(chave_produto(produto_id), json.dumps(dados, default=str), ex=settings.cache_ttl_segundos)


def invalidar_produto_no_cache(produto_id: int) -> None:
    """Remove ativamente uma entrada de produto no Redis (usado em UPDATE e DELETE)."""
    r.delete(chave_produto(produto_id))
