"""
app/routers/clientes_router.py
=================================
Rotas do domínio "clientes" (CRUD completo), extraídas do antigo
api.py. Nasce sob o prefixo /clientes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional

import cache
import crud
import filas
from app.dependencies import get_usuario_atual, exigir_admin
from app.limiter import limiter
from app.schemas.cliente_schemas import ClienteEntrada, ClienteAtualizacao

router = APIRouter(prefix="/clientes", tags=["Clientes"])

_COLUNAS = ["id", "nome", "email", "telefone", "data_nascimento", "endereco", "criado_em"]


@router.get("")
@limiter.limit("60/minute")
def listar(
    request: Request,
    usuario: dict = Depends(get_usuario_atual),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    nome: Optional[str] = Query(None),
):
    offset = (pagina - 1) * tamanho_pagina
    linhas = crud.listar_clientes(limite=tamanho_pagina, offset=offset, nome=nome)
    total = crud.contar_clientes(nome=nome)
    clientes = [dict(zip(_COLUNAS, linha)) for linha in linhas]

    return {
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total_de_clientes": total,
        "total_de_paginas": (total + tamanho_pagina - 1) // tamanho_pagina,
        "clientes": clientes,
    }


@router.get("/{cliente_id}")
def buscar(cliente_id: int, usuario: dict = Depends(get_usuario_atual)):
    cliente_cacheado = cache.buscar_cliente_no_cache(cliente_id)
    if cliente_cacheado is not None:
        return {**cliente_cacheado, "_origem": "cache"}

    linha = crud.buscar_cliente_por_id(cliente_id)
    if linha is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente = dict(zip(_COLUNAS, linha))
    cache.salvar_cliente_no_cache(cliente_id, cliente)
    return {**cliente, "_origem": "banco"}


@router.post("", status_code=201)
def criar(cliente: ClienteEntrada, usuario: dict = Depends(get_usuario_atual)):
    try:
        novo_id = crud.criar_cliente(
            nome=cliente.nome,
            email=cliente.email,
            telefone=cliente.telefone,
            data_nascimento=cliente.data_nascimento,
            endereco=cliente.endereco,
        )
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))

    try:
        filas.publicar_boas_vindas(novo_id, cliente.nome, cliente.email)
    except Exception as erro:
        print(f"Não foi possível publicar na fila (cliente foi criado normalmente): {erro}")

    return {"id": novo_id, "mensagem": "Cliente criado com sucesso"}


@router.patch("/{cliente_id}")
def atualizar(cliente_id: int, dados: ClienteAtualizacao, usuario: dict = Depends(get_usuario_atual)):
    linhas_alteradas = crud.atualizar_cliente(
        cliente_id, nome=dados.nome, telefone=dados.telefone, endereco=dados.endereco,
    )
    if linhas_alteradas == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cache.invalidar_cliente_no_cache(cliente_id)
    return {"mensagem": "Cliente atualizado com sucesso"}


@router.delete("/{cliente_id}")
def deletar(cliente_id: int, usuario: dict = Depends(exigir_admin)):
    """Só ADMIN pode deletar (RBAC)."""
    linhas_apagadas = crud.deletar_cliente(cliente_id)
    if linhas_apagadas == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cache.invalidar_cliente_no_cache(cliente_id)
    return {"mensagem": "Cliente apagado com sucesso"}
