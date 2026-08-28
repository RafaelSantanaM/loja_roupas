"""
app/routers/pedidos_router.py
==============================
Rotas do domínio "pedidos" (Checkout de compras, transações ACID e histórico).
Garante controle de estoque concorrente, invalidação de cache e disparo assíncrono de notificações via RabbitMQ.
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.core import cache
from app.core.logger import logger
from app.dependencies import get_usuario_atual
from app.limiter import limiter
from app.messaging import email_producer
from app.repositories import pedido_repo
from app.schemas.pedido_schemas import PedidoEntrada, PedidoResposta

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

_COLUNAS = ["id", "cliente_id", "produto_id", "quantidade", "valor_total", "criado_em"]


@router.post("", response_model=PedidoResposta, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def criar_pedido(
    request: Request,
    dados: PedidoEntrada,
    usuario: dict = Depends(get_usuario_atual),
):
    """
    Realiza o checkout de compra de um produto por um cliente.
    Executa transação ACID com trava pessimista (SELECT FOR UPDATE) no banco,
    invalida o cache de estoque do produto e enfileira e-mail de confirmação no RabbitMQ.
    """
    try:
        pedido_id, valor_total, nome_produto, nome_cliente, email_cliente = pedido_repo.criar_pedido(
            cliente_id=dados.cliente_id,
            produto_id=dados.produto_id,
            quantidade=dados.quantidade,
        )
    except pedido_repo.ClienteNaoEncontradoError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except pedido_repo.ProdutoNaoEncontradoError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except pedido_repo.EstoqueInsuficienteError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))
    except Exception as erro:
        logger.error(f"Erro inesperado ao processar pedido: {erro}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar pedido.",
        )

    # Invalida o cache Redis do produto, pois o estoque foi alterado no banco
    cache.invalidar_produto_no_cache(dados.produto_id)

    # Dispara a mensagem assíncrona para envio do comprovante por e-mail
    try:
        email_producer.publicar_confirmacao_pedido(
            pedido_id=pedido_id,
            cliente_id=dados.cliente_id,
            nome_cliente=nome_cliente,
            email_cliente=email_cliente,
            nome_produto=nome_produto,
            quantidade=dados.quantidade,
            valor_total=valor_total,
        )
    except Exception as erro_fila:
        # Se a fila falhar, a transação bancária já foi salva com sucesso; não quebramos o checkout
        logger.warning(f"Falha ao publicar confirmação de pedido na fila RabbitMQ: {erro_fila}")

    return {
        "id": pedido_id,
        "cliente_id": dados.cliente_id,
        "produto_id": dados.produto_id,
        "quantidade": dados.quantidade,
        "valor_total": valor_total,
        "criado_em": datetime.now(timezone.utc),
    }


@router.get("")
@limiter.limit("60/minute")
def listar_pedidos(
    request: Request,
    usuario: dict = Depends(get_usuario_atual),
    pagina: int = Query(1, ge=1, description="Número da página"),
    tamanho_pagina: int = Query(10, ge=1, le=100, description="Itens por página"),
    cliente_id: Optional[int] = Query(None, description="Filtro opcional por cliente"),
):
    """Lista o histórico de pedidos paginado com filtro opcional por ID do cliente."""
    offset = (pagina - 1) * tamanho_pagina
    linhas = pedido_repo.listar_pedidos(limite=tamanho_pagina, offset=offset, cliente_id=cliente_id)
    total = pedido_repo.contar_pedidos(cliente_id=cliente_id)
    pedidos = [dict(zip(_COLUNAS, linha)) for linha in linhas]

    return {
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total_de_pedidos": total,
        "total_de_paginas": (total + tamanho_pagina - 1) // tamanho_pagina,
        "pedidos": pedidos,
    }


@router.get("/{pedido_id}")
def buscar_pedido(
    pedido_id: int,
    usuario: dict = Depends(get_usuario_atual),
):
    """Busca os detalhes de um pedido específico por ID."""
    linha = pedido_repo.buscar_pedido_por_id(pedido_id)
    if linha is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")

    return dict(zip(_COLUNAS, linha))
