"""
tests/test_api_integration.py
===============================
TESTES DE INTEGRAÇÃO -- passam pela aplicação inteira: FastAPI,
autenticação, RBAC, e o banco de dados Postgres REAL configurado
no seu .env.

RESSALVA DE ENGENHARIA, seja honesto sobre isso: o ideal, em um
ambiente profissional maduro, é rodar testes de integração contra um
banco de dados DEDICADO a testes (isolado do banco de desenvolvimento),
recriado do zero a cada execução -- evitando que um teste com bug
"suje" dados que você está usando manualmente para explorar a API.
Aqui, por pragmatismo do estudo, usamos o mesmo banco `loja_roupas`,
com o cuidado de:
  1) usar e-mails únicos (uuid) para nunca colidir com dados existentes
  2) fazer cleanup explícito (deletar o que foi criado) dentro do teste
"""

import uuid

import pytest


def _email_unico() -> str:
    """Gera um e-mail garantidamente novo, evitando colisão com a UNIQUE constraint."""
    return f"pytest_{uuid.uuid4().hex[:10]}@example.com"


# ---------------------------------------------------------
# Autenticação básica
# ---------------------------------------------------------

def test_endpoint_raiz_nao_exige_autenticacao(client):
    resposta = client.get("/")
    assert resposta.status_code == 200


def test_listar_clientes_sem_token_retorna_401(client):
    resposta = client.get("/clientes")
    assert resposta.status_code == 401


def test_listar_clientes_com_token_invalido_retorna_401(client):
    resposta = client.get("/clientes", headers={"Authorization": "Bearer token.completamente.invalido"})
    assert resposta.status_code == 401


# ---------------------------------------------------------
# RBAC (autorização por papel)
# ---------------------------------------------------------

def test_funcionario_pode_listar_clientes(client, funcionario_token):
    """RBAC deve LIBERAR leitura para qualquer usuário autenticado."""
    headers = {"Authorization": f"Bearer {funcionario_token}"}
    resposta = client.get("/clientes", headers=headers)
    assert resposta.status_code == 200


def test_funcionario_nao_pode_deletar_cliente(client, admin_token, funcionario_token):
    """RBAC deve BLOQUEAR delete para papel 'funcionario' -- 403, não 401."""
    # Arrange: cria um cliente descartável (como admin, pra garantir que a criação funcione)
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    resposta = client.post(
        "/clientes", headers=headers_admin,
        json={"nome": "RBAC Teste", "email": _email_unico()},
    )
    assert resposta.status_code == 201
    cliente_id = resposta.json()["id"]

    # Act: tenta deletar como funcionário comum
    headers_func = {"Authorization": f"Bearer {funcionario_token}"}
    resposta = client.delete(f"/clientes/{cliente_id}", headers=headers_func)

    # Assert
    assert resposta.status_code == 403

    # Cleanup: remove de fato, usando admin
    client.delete(f"/clientes/{cliente_id}", headers=headers_admin)


def test_admin_pode_deletar_cliente(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resposta = client.post(
        "/clientes", headers=headers,
        json={"nome": "Admin Delete Teste", "email": _email_unico()},
    )
    cliente_id = resposta.json()["id"]

    resposta = client.delete(f"/clientes/{cliente_id}", headers=headers)
    assert resposta.status_code == 200


# ---------------------------------------------------------
# Ciclo CRUD completo
# ---------------------------------------------------------

def test_ciclo_crud_completo_de_cliente(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    email = _email_unico()

    # CREATE
    resposta = client.post(
        "/clientes", headers=headers,
        json={"nome": "Cliente Pytest", "email": email},
    )
    assert resposta.status_code == 201
    cliente_id = resposta.json()["id"]

    # READ
    resposta = client.get(f"/clientes/{cliente_id}", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["email"] == email

    # UPDATE
    resposta = client.patch(
        f"/clientes/{cliente_id}", headers=headers,
        json={"telefone": "11999990000"},
    )
    assert resposta.status_code == 200

    resposta = client.get(f"/clientes/{cliente_id}", headers=headers)
    assert resposta.json()["telefone"] == "11999990000"

    # DELETE (cleanup dentro do próprio teste)
    resposta = client.delete(f"/clientes/{cliente_id}", headers=headers)
    assert resposta.status_code == 200

    # Confirma que realmente sumiu
    resposta = client.get(f"/clientes/{cliente_id}", headers=headers)
    assert resposta.status_code == 404


def test_criar_cliente_com_email_duplicado_retorna_400(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    email = _email_unico()

    resposta1 = client.post("/clientes", headers=headers, json={"nome": "Original", "email": email})
    assert resposta1.status_code == 201
    cliente_id = resposta1.json()["id"]

    # Act: tenta criar OUTRO cliente com o MESMO e-mail
    resposta2 = client.post("/clientes", headers=headers, json={"nome": "Duplicado", "email": email})

    # Assert
    assert resposta2.status_code == 400

    # Cleanup
    client.delete(f"/clientes/{cliente_id}", headers=headers)


def test_buscar_cliente_inexistente_retorna_404(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resposta = client.get("/clientes/999999999", headers=headers)
    assert resposta.status_code == 404


# ---------------------------------------------------------
# Refresh token
# ---------------------------------------------------------

def test_fluxo_refresh_token_com_rotacao(client):
    """Valida Refresh Token Rotation: emite novos tokens e invalida o anterior."""
    resposta_login = client.post("/auth/login", data={"username": "gerente", "password": "senha123"})
    refresh_token_1 = resposta_login.json()["refresh_token"]

    # 1. Primeiro refresh com sucesso
    resposta_refresh_1 = client.post("/auth/refresh", json={"refresh_token": refresh_token_1})
    assert resposta_refresh_1.status_code == 200
    dados_refresh = resposta_refresh_1.json()
    assert "access_token" in dados_refresh
    assert "refresh_token" in dados_refresh
    refresh_token_2 = dados_refresh["refresh_token"]
    assert refresh_token_2 != refresh_token_1

    # 2. Tentar reutilizar o refresh_token_1 deve falhar (Token Replay Attack prevenido)
    resposta_reuso = client.post("/auth/refresh", json={"refresh_token": refresh_token_1})
    assert resposta_reuso.status_code == 401

    # 3. Usar o novo refresh_token_2 deve funcionar perfeitamente
    resposta_refresh_2 = client.post("/auth/refresh", json={"refresh_token": refresh_token_2})
    assert resposta_refresh_2.status_code == 200
    assert "access_token" in resposta_refresh_2.json()


def test_logout_revoga_refresh_token(client):
    # Arrange: login novo, exclusivo pra esse teste
    resposta_login = client.post("/auth/login", data={"username": "gerente", "password": "senha123"})
    refresh_token = resposta_login.json()["refresh_token"]

    # Act 1: revoga
    resposta_logout = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert resposta_logout.status_code == 200

    # Act 2: tenta usar o MESMO refresh token, já revogado
    resposta_refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    # Assert: deve ser recusado, mesmo com assinatura JWT ainda matematicamente válida
    assert resposta_refresh.status_code == 401

