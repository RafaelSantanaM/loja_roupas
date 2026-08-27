"""
app/routers/produtos_router.py
================================
Rotas do domínio "produtos" (Catálogo e estoque da loja de roupas).
Suporta listagem paginada, busca acelerada por cache Redis e mutações restritas a administradores (RBAC).
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core import cache
from app.repositories import produto_repo
from app.dependencies import get_usuario_atual, exigir_admin
from app.limiter import limiter
from app.schemas.produto_schemas import ProdutoEntrada, ProdutoAtualizacao

router = APIRouter(prefix="/produtos", tags=["Produtos"])

_COLUNAS = ["id", "nome", "preco", "estoque"]


@router.get("")
@limiter.limit("60/minute")
def listar_produtos(
    request: Request,
    usuario: dict = Depends(get_usuario_atual),
    pagina: int = Query(1, ge=1, description="Número da página"),
    tamanho_pagina: int = Query(10, ge=1, le=100, description="Itens por página"),
    nome: Optional[str] = Query(None, description="Filtro opcional por nome da peça"),
):
    """Lista produtos do catálogo com suporte a paginação e filtro por nome."""
    offset = (pagina - 1) * tamanho_pagina
    linhas = produto_repo.listar_produtos(limite=tamanho_pagina, offset=offset, nome=nome)
    total = produto_repo.contar_produtos(nome=nome)
    produtos = [dict(zip(_COLUNAS, linha)) for linha in linhas]

    return {
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total_de_produtos": total,
        "total_de_paginas": (total + tamanho_pagina - 1) // tamanho_pagina,
        "produtos": produtos,
    }


@router.get("/{produto_id}")
def buscar_produto(
    produto_id: int,
    usuario: dict = Depends(get_usuario_atual),
):
    """Busca um produto por ID, consultando primeiramente o cache em memória (Redis)."""
    produto_cacheado = cache.buscar_produto_no_cache(produto_id)
    if produto_cacheado is not None:
        return {**produto_cacheado, "_origem": "cache"}

    linha = produto_repo.buscar_produto_por_id(produto_id)
    if linha is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto = dict(zip(_COLUNAS, linha))
    # Converte tipos numéricos (Decimal/float) para serialização JSON no Redis
    produto_serializavel = {**produto, "preco": float(produto["preco"])}
    cache.salvar_produto_no_cache(produto_id, produto_serializavel)

    return {**produto_serializavel, "_origem": "banco"}


@router.post("", status_code=201)
def criar_produto(
    dados: ProdutoEntrada,
    usuario: dict = Depends(exigir_admin),
):
    """Cadastra uma nova peça de roupa no catálogo (Apenas Administradores)."""
    try:
        novo_id = produto_repo.criar_produto(
            nome=dados.nome,
            preco=dados.preco,
            estoque=dados.estoque,
        )
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))

    return {"id": novo_id, "mensagem": "Produto criado com sucesso"}


@router.patch("/{produto_id}")
def atualizar_produto(
    produto_id: int,
    dados: ProdutoAtualizacao,
    usuario: dict = Depends(exigir_admin),
):
    """Atualiza dados cadastrais ou estoque do produto e invalida o cache (Apenas Administradores)."""
    linhas_alteradas = produto_repo.atualizar_produto(
        produto_id=produto_id,
        nome=dados.nome,
        preco=dados.preco,
        estoque=dados.estoque,
    )
    if linhas_alteradas == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    cache.invalidar_produto_no_cache(produto_id)
    return {"mensagem": "Produto atualizado com sucesso"}


@router.delete("/{produto_id}")
def deletar_produto(
    produto_id: int,
    usuario: dict = Depends(exigir_admin),
):
    """Remove um produto do catálogo e invalida o cache (Apenas Administradores)."""
    try:
        linhas_apagadas = produto_repo.deletar_produto(produto_id)
    except Exception as erro:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir produto com histórico de pedidos vinculados.",
        )

    if linhas_apagadas == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    cache.invalidar_produto_no_cache(produto_id)
    return {"mensagem": "Produto apagado com sucesso"}
