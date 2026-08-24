"""
app/core/cache.py
===================
Camada de cache usando Redis.

Antes deste commit, este arquivo era cache.py, solto na raiz do
projeto. Movido para app/core/ pelo mesmo motivo de security.py:
é uma preocupação transversal, usada só pelo domínio de clientes
hoje, mas conceitualmente não pertence a nenhum domínio específico.

O CONTEÚDO não mudou -- só o endereço.
"""

import json
import redis

from app.core.config import settings

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


def chave_cliente(cliente_id: int) -> str:
    """Padroniza o formato da chave -- evita erro de digitação espalhado pelo código."""
    return f"cliente:{cliente_id}"


def buscar_cliente_no_cache(cliente_id: int):
    """Retorna o dicionário do cliente se estiver em cache, ou None (cache miss)."""
    valor = r.get(chave_cliente(cliente_id))
    if valor is None:
        return None
    return json.loads(valor)


def salvar_cliente_no_cache(cliente_id: int, dados: dict) -> None:
    """Grava o cliente no cache, com expiração automática (TTL)."""
    r.set(chave_cliente(cliente_id), json.dumps(dados, default=str), ex=settings.cache_ttl_segundos)


def invalidar_cliente_no_cache(cliente_id: int) -> None:
    """Remove ativamente uma entrada -- usado em UPDATE e DELETE."""
    r.delete(chave_cliente(cliente_id))
