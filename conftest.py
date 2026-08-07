"""
tests/conftest.py
==================
Arquivo especial reconhecido automaticamente pelo pytest. Define
"fixtures" -- recursos preparados ANTES dos testes rodarem, e
reutilizáveis entre vários arquivos de teste.

Analogia: se cada teste fosse uma receita de bolo, as fixtures são
os ingredientes já pesados e separados na bancada, prontos pra usar,
em vez de cada receita pesar tudo de novo do zero.
"""

import pytest
from fastapi.testclient import TestClient

from api import app


@pytest.fixture(scope="session")
def client():
    """
    Cliente de teste que simula requisições HTTP contra a API,
    SEM precisar de um servidor uvicorn rodando de verdade -- o
    TestClient chama a aplicação ASGI diretamente em memória.

    scope="session" -> essa fixture é criada UMA vez só, e reaproveitada
    por todos os testes da execução (mais rápido que recriar a cada teste).

    IMPORTANTE: desligamos o rate limiter aqui. Isso é uma decisão
    deliberada, documentada -- testes de lógica de negócio não devem
    ser afetados por um controle de infraestrutura que existe para
    proteger contra abuso externo, não para limitar nossa própria
    suíte de testes.
    """
    app.state.limiter.enabled = False
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def admin_token(client):
    """Token de acesso de um usuário com papel 'admin' (usuário 'gerente')."""
    resposta = client.post("/login", data={"username": "gerente", "password": "senha123"})
    assert resposta.status_code == 200, "Pré-condição falhou: usuário 'gerente' precisa existir (rode usuarios_crud.py)"
    return resposta.json()["access_token"]


@pytest.fixture(scope="session")
def funcionario_token(client):
    """Token de acesso de um usuário com papel 'funcionario' (usuário 'vendedor')."""
    resposta = client.post("/login", data={"username": "vendedor", "password": "senha123"})
    assert resposta.status_code == 200, "Pré-condição falhou: usuário 'vendedor' precisa existir (rode usuarios_crud.py)"
    return resposta.json()["access_token"]
