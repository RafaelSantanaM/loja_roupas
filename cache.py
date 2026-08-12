"""
cache.py
========
Camada de cache usando Redis. Centralizamos aqui a lógica de
get/set/invalidate, para não espalhar detalhes de Redis pelo crud.py.
"""

import json
import redis

# decode_responses=True -> o Redis devolve strings Python normais,
# em vez de bytes (b"..."), facilitando o uso direto.
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

TTL_SEGUNDOS = 60  # tempo de vida do cache: 60 segundos


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
    r.set(chave_cliente(cliente_id), json.dumps(dados, default=str), ex=TTL_SEGUNDOS)


def invalidar_cliente_no_cache(cliente_id: int) -> None:
    """Remove ativamente uma entrada -- usado em UPDATE e DELETE."""
    r.delete(chave_cliente(cliente_id))
