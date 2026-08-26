"""
app/schemas/produto_schemas.py
================================
Schemas Pydantic para validação e serialização do catálogo de produtos.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ProdutoEntrada(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome da peça de roupa")
    preco: float = Field(..., gt=0, description="Preço unitário em reais (deve ser positivo)")
    estoque: int = Field(0, ge=0, description="Quantidade disponível no estoque")


class ProdutoAtualizacao(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    preco: Optional[float] = Field(None, gt=0)
    estoque: Optional[int] = Field(None, ge=0)
