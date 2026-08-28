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

from app.db.session import get_connection


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


# ---------------------------------------------------------
# Observabilidade & Health Check
# ---------------------------------------------------------

def test_health_check_retorna_status_200_e_servicos_saudaveis(client):
    """Verifica se o endpoint GET /health checa ativamente Postgres, Redis e RabbitMQ."""
    resposta = client.get("/health")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["status"] == "healthy"
    assert dados["servicos"]["postgres"] == "ok"
    assert dados["servicos"]["redis"] == "ok"
    assert dados["servicos"]["rabbitmq"] == "ok"


def test_middleware_injeta_x_request_id_na_resposta(client):
    """Verifica se cada resposta HTTP carrega o correlation ID (X-Request-ID)."""
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "x-request-id" in resposta.headers
    assert len(resposta.headers["x-request-id"]) > 0


def test_middleware_preserva_x_request_id_enviado_pelo_cliente(client):
    """Se o cliente enviar um correlation ID customizado, a API deve preservá-lo."""
    custom_id = "correlation-trace-12345"
    resposta = client.get("/", headers={"X-Request-ID": custom_id})
    assert resposta.status_code == 200
    assert resposta.headers.get("x-request-id") == custom_id


# ---------------------------------------------------------
# Domínio: Produtos (Catálogo, Cache Redis & RBAC)
# ---------------------------------------------------------

def test_funcionario_pode_listar_produtos(client, funcionario_token):
    """Qualquer usuário autenticado (incluindo funcionários) pode consultar o catálogo."""
    headers = {"Authorization": f"Bearer {funcionario_token}"}
    resposta = client.get("/produtos", headers=headers)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "produtos" in dados
    assert "total_de_produtos" in dados


def test_funcionario_nao_pode_criar_produto(client, funcionario_token):
    """Apenas administradores podem cadastrar novos produtos (RBAC: 403 Forbidden)."""
    headers = {"Authorization": f"Bearer {funcionario_token}"}
    resposta = client.post(
        "/produtos",
        headers=headers,
        json={"nome": "Vestido Floral", "preco": 129.90, "estoque": 5},
    )
    assert resposta.status_code == 403


def test_ciclo_produto_com_cache_redis_e_rbac(client, admin_token):
    """Valida CRUD de produto por admin, cache miss (banco), cache hit (redis) e invalidação."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. CREATE (Admin)
    resposta_create = client.post(
        "/produtos",
        headers=headers,
        json={"nome": "Jaqueta Jeans Pytest", "preco": 199.90, "estoque": 12},
    )
    assert resposta_create.status_code == 201
    produto_id = resposta_create.json()["id"]

    # 2. READ 1: Primeira leitura busca no Banco e popula o Redis (Cache Miss)
    resposta_read1 = client.get(f"/produtos/{produto_id}", headers=headers)
    assert resposta_read1.status_code == 200
    assert resposta_read1.json()["_origem"] == "banco"
    assert resposta_read1.json()["nome"] == "Jaqueta Jeans Pytest"

    # 3. READ 2: Segunda leitura vem direto do Redis (Cache Hit)
    resposta_read2 = client.get(f"/produtos/{produto_id}", headers=headers)
    assert resposta_read2.status_code == 200
    assert resposta_read2.json()["_origem"] == "cache"

    # 4. UPDATE: Atualização deve invalidar a chave no Redis
    resposta_update = client.patch(
        f"/produtos/{produto_id}",
        headers=headers,
        json={"preco": 179.90, "estoque": 25},
    )
    assert resposta_update.status_code == 200

    # 5. READ 3: Leitura após update busca dados atualizados no Banco (Cache Miss novamente)
    resposta_read3 = client.get(f"/produtos/{produto_id}", headers=headers)
    assert resposta_read3.status_code == 200
    assert resposta_read3.json()["_origem"] == "banco"
    assert float(resposta_read3.json()["preco"]) == 179.90
    assert resposta_read3.json()["estoque"] == 25

    # 6. DELETE: Cleanup e invalidação
    resposta_delete = client.delete(f"/produtos/{produto_id}", headers=headers)
    assert resposta_delete.status_code == 200

    # 7. READ 4: Não deve mais existir (404)
    resposta_read4 = client.get(f"/produtos/{produto_id}", headers=headers)
    assert resposta_read4.status_code == 404


# ---------------------------------------------------------
# Domínio: Pedidos (Checkout ACID, Concorrência & Estoque)
# ---------------------------------------------------------

def test_checkout_pedido_com_sucesso_debita_estoque(client, admin_token, funcionario_token):
    """Valida compra com sucesso, cálculo correto do valor total e débito atômico de estoque."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_func = {"Authorization": f"Bearer {funcionario_token}"}

    # 1. Arrange: Cria cliente e produto de teste
    res_cli = client.post(
        "/clientes",
        headers=headers_admin,
        json={"nome": "Cliente Checkout", "email": _email_unico()},
    )
    cliente_id = res_cli.json()["id"]

    res_prod = client.post(
        "/produtos",
        headers=headers_admin,
        json={"nome": "Calça Alfaiataria Pytest", "preco": 150.00, "estoque": 10},
    )
    produto_id = res_prod.json()["id"]

    try:
        # 2. Act: Realiza pedido de 3 unidades
        res_pedido = client.post(
            "/pedidos",
            headers=headers_func,
            json={"cliente_id": cliente_id, "produto_id": produto_id, "quantidade": 3},
        )
        assert res_pedido.status_code == 201
        dados_pedido = res_pedido.json()
        assert dados_pedido["quantidade"] == 3
        assert float(dados_pedido["valor_total"]) == 450.00
        pedido_id = dados_pedido["id"]

        # 3. Assert: Estoque do produto deve ter caído de 10 para 7
        res_prod_atual = client.get(f"/produtos/{produto_id}", headers=headers_admin)
        assert res_prod_atual.status_code == 200
        assert res_prod_atual.json()["estoque"] == 7

        # 4. Assert: Busca pedido por ID
        res_get_ped = client.get(f"/pedidos/{pedido_id}", headers=headers_func)
        assert res_get_ped.status_code == 200
        assert res_get_ped.json()["id"] == pedido_id

        # 5. Assert: Tentar deletar o produto com pedido associado deve falhar (400)
        res_del_prod_fail = client.delete(f"/produtos/{produto_id}", headers=headers_admin)
        assert res_del_prod_fail.status_code == 400
        assert "histórico de pedidos" in res_del_prod_fail.json()["detail"]

    finally:
        # Cleanup: Remove primeiro o pedido da tabela 'pedidos' para liberar as FKs
        if "pedido_id" in locals() and pedido_id:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM pedidos WHERE id = %s;", (pedido_id,))
                conn.commit()

        client.delete(f"/produtos/{produto_id}", headers=headers_admin)
        client.delete(f"/clientes/{cliente_id}", headers=headers_admin)


def test_checkout_rejeita_pedido_com_estoque_insuficiente(client, admin_token, funcionario_token):
    """Garante integridade ACID: Se o estoque for menor que o pedido, a compra é rejeitada e o estoque não muda."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_func = {"Authorization": f"Bearer {funcionario_token}"}

    res_cli = client.post(
        "/clientes",
        headers=headers_admin,
        json={"nome": "Cliente Estoque Zero", "email": _email_unico()},
    )
    cliente_id = res_cli.json()["id"]

    res_prod = client.post(
        "/produtos",
        headers=headers_admin,
        json={"nome": "Shorts Praia Pytest", "preco": 80.00, "estoque": 2},
    )
    produto_id = res_prod.json()["id"]

    try:
        # Tenta comprar 5 unidades (só temos 2)
        res_pedido = client.post(
            "/pedidos",
            headers=headers_func,
            json={"cliente_id": cliente_id, "produto_id": produto_id, "quantidade": 5},
        )
        assert res_pedido.status_code == 400
        assert "Estoque insuficiente" in res_pedido.json()["detail"]

        # Verifica que o estoque continuou exatamente 2 (Rollback da transação)
        res_prod_atual = client.get(f"/produtos/{produto_id}", headers=headers_admin)
        assert res_prod_atual.json()["estoque"] == 2

    finally:
        client.delete(f"/produtos/{produto_id}", headers=headers_admin)
        client.delete(f"/clientes/{cliente_id}", headers=headers_admin)


def test_checkout_rejeita_entidades_inexistentes(client, funcionario_token):
    """Retorna 404 ao tentar checkout com cliente ou produto que não existe."""
    headers = {"Authorization": f"Bearer {funcionario_token}"}

    # Cliente inexistente
    res1 = client.post(
        "/pedidos",
        headers=headers,
        json={"cliente_id": 9999999, "produto_id": 1, "quantidade": 1},
    )
    assert res1.status_code == 404

    # Produto inexistente
    res2 = client.post(
        "/pedidos",
        headers=headers,
        json={"cliente_id": 1, "produto_id": 9999999, "quantidade": 1},
    )
    assert res2.status_code == 404


# ---------------------------------------------------------
# Segurança Ofensiva & Hardening OWASP
# ---------------------------------------------------------

def test_headers_de_seguranca_owasp_presentes_na_resposta(client):
    """Garante injeção de cabeçalhos de segurança OWASP em todas as respostas HTTP."""
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.headers.get("x-content-type-options") == "nosniff"
    assert resposta.headers.get("x-frame-options") == "DENY"
    assert "strict-transport-security" in resposta.headers
    assert resposta.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert resposta.headers.get("x-xss-protection") == "1; mode=block"


def test_schema_cliente_rejeita_payload_com_nome_ou_endereco_gigante(client, admin_token):
    """Garante defesa contra DoS por payload gigante, rejeitando campos que excedem max_length."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Nome com mais de 100 caracteres
    resposta = client.post(
        "/clientes",
        headers=headers,
        json={"nome": "A" * 105, "email": _email_unico()},
    )
    assert resposta.status_code == 422

    # Endereço com mais de 255 caracteres
    resposta_end = client.post(
        "/clientes",
        headers=headers,
        json={"nome": "Cliente Valido", "email": _email_unico(), "endereco": "B" * 300},
    )
    assert resposta_end.status_code == 422





