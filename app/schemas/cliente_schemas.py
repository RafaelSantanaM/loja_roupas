"""
app/schemas/cliente_schemas.py
================================
Os "moldes" Pydantic de validação de clientes, extraídos do meio do
antigo api.py. Antes, eles ficavam misturados junto com os endpoints
no mesmo arquivo; separar deixa claro, só de olhar a pasta, "qual é o
formato de dado que a API de clientes espera receber/devolver".
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ClienteEntrada(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo do cliente")
    email: EmailStr = Field(..., description="E-mail único do cliente")
    telefone: Optional[str] = Field(None, max_length=20, description="Número de telefone com DDD")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento")
    endereco: Optional[str] = Field(None, max_length=255, description="Endereço de entrega")


class ClienteAtualizacao(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=255)

