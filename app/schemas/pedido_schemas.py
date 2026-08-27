"""
app/schemas/pedido_schemas.py
===============================
Schemas Pydantic para validação e serialização do fluxo de compras e pedidos.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PedidoEntrada(BaseModel):
    cliente_id: int = Field(..., gt=0, description="ID do cliente que está realizando o pedido")
    produto_id: int = Field(..., gt=0, description="ID do produto sendo comprado")
    quantidade: int = Field(1, gt=0, le=1000, description="Quantidade de itens (mínimo 1, máximo 1000)")


class PedidoResposta(BaseModel):
    id: int
    cliente_id: int
    produto_id: int
    quantidade: int
    valor_total: float
    criado_em: datetime
