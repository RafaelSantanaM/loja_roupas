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

from pydantic import BaseModel, EmailStr


class ClienteEntrada(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    endereco: Optional[str] = None


class ClienteAtualizacao(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
