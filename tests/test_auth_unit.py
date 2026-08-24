"""
tests/test_auth_unit.py
========================
TESTES UNITÁRIOS -- testam app/core/security.py isoladamente, sem
tocar banco de dados nem rede.

Neste commit, o import muda de "from auth import (...)" para
"from app.core.security import (...)" -- os testes em si (o que
cada um valida) não mudam nada.
"""

from app.core.security import (
    gerar_hash_senha,
    conferir_senha,
    criar_access_token,
    criar_refresh_token,
    verificar_token,
)


def test_hash_nunca_e_igual_a_senha_original():
    hash_gerado = gerar_hash_senha("minhaSenha123")
    assert hash_gerado != "minhaSenha123"


def test_conferir_senha_aceita_senha_correta():
    hash_gerado = gerar_hash_senha("minhaSenha123")
    assert conferir_senha("minhaSenha123", hash_gerado) is True


def test_conferir_senha_rejeita_senha_incorreta():
    hash_gerado = gerar_hash_senha("minhaSenha123")
    assert conferir_senha("senhaCompletamenteErrada", hash_gerado) is False


def test_bcrypt_usa_salt_aleatorio():
    hash1 = gerar_hash_senha("mesmaSenha")
    hash2 = gerar_hash_senha("mesmaSenha")
    assert hash1 != hash2
    assert conferir_senha("mesmaSenha", hash1) is True
    assert conferir_senha("mesmaSenha", hash2) is True


def test_access_token_carrega_payload_correto():
    token = criar_access_token("usuario_teste", "admin")
    payload = verificar_token(token)
    assert payload["sub"] == "usuario_teste"
    assert payload["papel"] == "admin"
    assert payload["tipo"] == "access"


def test_refresh_token_gera_jti_unico_a_cada_chamada():
    _, jti1, _ = criar_refresh_token("usuario_teste")
    _, jti2, _ = criar_refresh_token("usuario_teste")
    assert jti1 != jti2


def test_verificar_token_rejeita_token_adulterado():
    token = criar_access_token("usuario_teste", "admin")
    token_adulterado = token[:-1] + ("A" if token[-1] != "A" else "B")
    try:
        verificar_token(token_adulterado)
        assert False, "Deveria ter levantado ValueError para token adulterado"
    except ValueError:
        pass
