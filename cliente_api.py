"""
cliente_api.py
===============
Um "cliente HTTP" de verdade, escrito em Python, que conversa com a
NOSSA PRÓPRIA API (api.py). É o mesmo que fizemos no curl, só que
agora em código -- o que significa que dá pra reaproveitar, repetir,
e combinar com lógica (loops, condições, etc).

Pré-requisito: a API precisa estar rodando em outro terminal:
    uvicorn api:app --reload

Como rodar este script:
    python cliente_api.py
"""

import requests

# URL base da nossa API. Definir isso como uma variável, em vez de
# repetir o endereço toda hora, é uma boa prática -- se um dia a API
# mudar de endereço, você só troca em UM lugar.
BASE_URL = "http://127.0.0.1:8000"


def fazer_login(username: str, senha: str) -> str:
    """
    Faz login na API e devolve o token JWT.

    Repare: aqui usamos o parâmetro 'data' (não 'json'), porque o
    endpoint /login espera um FORMULÁRIO (OAuth2PasswordRequestForm),
    igual fizemos no curl com -H "Content-Type: application/x-www-form-urlencoded"
    """
    resposta = requests.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": senha},
    )

    # Se o login falhar (usuário/senha errado), resposta.status_code
    # não vai ser 200 -- vamos checar isso explicitamente.
    if resposta.status_code != 200:
        raise Exception(f"Falha no login: {resposta.status_code} - {resposta.text}")

    dados = resposta.json()
    return dados["access_token"]


def criar_cliente(token: str, nome: str, email: str) -> dict:
    """Cria um cliente novo, autenticado com o token."""
    resposta = requests.post(
        f"{BASE_URL}/clientes",
        headers={"Authorization": f"Bearer {token}"},
        json={"nome": nome, "email": email},  # 'json=' já serializa e seta o Content-Type sozinho
    )
    resposta.raise_for_status()  # levanta um erro Python se vier 4xx/5xx
    return resposta.json()


def listar_clientes(token: str, pagina: int = 1, tamanho_pagina: int = 10) -> dict:
    """Lista clientes, usando query string (parâmetros passados em 'params')."""
    resposta = requests.get(
        f"{BASE_URL}/clientes",
        headers={"Authorization": f"Bearer {token}"},
        params={"pagina": pagina, "tamanho_pagina": tamanho_pagina},
    )
    resposta.raise_for_status()
    return resposta.json()


def atualizar_cliente(token: str, cliente_id: int, telefone: str) -> dict:
    """Atualiza um campo específico de um cliente (PATCH)."""
    resposta = requests.patch(
        f"{BASE_URL}/clientes/{cliente_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"telefone": telefone},
    )
    resposta.raise_for_status()
    return resposta.json()


def deletar_cliente(token: str, cliente_id: int) -> dict:
    """Apaga um cliente."""
    resposta = requests.delete(
        f"{BASE_URL}/clientes/{cliente_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    resposta.raise_for_status()
    return resposta.json()


if __name__ == "__main__":
    print("1) Fazendo login...")
    token = fazer_login("admin", "senha123")
    print(f"   Token recebido (primeiros 20 caracteres): {token[:20]}...\n")

    print("2) Criando um cliente novo...")
    novo = criar_cliente(token, nome="Cliente via Python", email="python@example.com")
    cliente_id = novo["id"]
    print(f"   Cliente criado com id={cliente_id}\n")

    print("3) Listando clientes (página 1)...")
    pagina = listar_clientes(token, pagina=1, tamanho_pagina=5)
    print(f"   Total de clientes: {pagina['total_de_clientes']}")
    for c in pagina["clientes"]:
        print(f"   - {c['id']}: {c['nome']} ({c['email']})")
    print()

    print(f"4) Atualizando o telefone do cliente {cliente_id}...")
    atualizar_cliente(token, cliente_id, telefone="11912345678")
    print("   Atualizado!\n")

    print(f"5) Apagando o cliente {cliente_id}...")
    deletar_cliente(token, cliente_id)
    print("   Apagado!\n")

    print("6) Tentando buscar um cliente que não existe (pra ver o erro)...")
    try:
        resposta = requests.get(
            f"{BASE_URL}/clientes/999999",
            headers={"Authorization": f"Bearer {token}"},
        )
        resposta.raise_for_status()
    except requests.exceptions.HTTPError as erro:
        print(f"   Erro esperado capturado: {erro}")
