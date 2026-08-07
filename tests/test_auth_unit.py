"""
tests/test_auth_unit.py
========================
TESTES UNITÁRIOS -- testam auth.py isoladamente, sem tocar banco de
dados nem rede. Cada teste segue o padrão AAA (Arrange-Act-Assert).
"""

from auth import (
    gerar_hash_senha,
    conferir_senha,
    criar_access_token,
    criar_refresh_token,
    verificar_token,
)


def test_hash_nunca_e_igual_a_senha_original():
    """Propriedade de segurança fundamental: o hash não pode ser a senha em texto puro."""
    # Arrange + Act
    hash_gerado = gerar_hash_senha("minhaSenha123")

    # Assert
    assert hash_gerado != "minhaSenha123"


def test_conferir_senha_aceita_senha_correta():
    # Arrange
    hash_gerado = gerar_hash_senha("minhaSenha123")

    # Act
    resultado = conferir_senha("minhaSenha123", hash_gerado)

    # Assert
    assert resultado is True


def test_conferir_senha_rejeita_senha_incorreta():
    # Arrange
    hash_gerado = gerar_hash_senha("minhaSenha123")

    # Act
    resultado = conferir_senha("senhaCompletamenteErrada", hash_gerado)

    # Assert
    assert resultado is False


def test_bcrypt_usa_salt_aleatorio():
    """
    Propriedade importante do bcrypt: a MESMA senha, hasheada duas vezes,
    produz hashes DIFERENTES (por causa do "salt" aleatório embutido).
    Isso impede um ataque de "rainbow table" (tabela pré-computada de
    hashes conhecidos) -- se testássemos apenas "hash1 == hash2", estaríamos
    validando o comportamento ERRADO.
    """
    hash1 = gerar_hash_senha("mesmaSenha")
    hash2 = gerar_hash_senha("mesmaSenha")

    assert hash1 != hash2
    # mas ambos devem continuar validando a senha original corretamente:
    assert conferir_senha("mesmaSenha", hash1) is True
    assert conferir_senha("mesmaSenha", hash2) is True


def test_access_token_carrega_payload_correto():
    # Arrange + Act
    token = criar_access_token("usuario_teste", "admin")
    payload = verificar_token(token)

    # Assert
    assert payload["sub"] == "usuario_teste"
    assert payload["papel"] == "admin"
    assert payload["tipo"] == "access"


def test_refresh_token_gera_jti_unico_a_cada_chamada():
    """
    O jti (JWT ID) precisa ser único por token gerado -- é a base de
    todo o mecanismo de revogação. Se dois tokens compartilhassem o
    mesmo jti, revogar um revogaria os dois.
    """
    _, jti1, _ = criar_refresh_token("usuario_teste")
    _, jti2, _ = criar_refresh_token("usuario_teste")

    assert jti1 != jti2


def test_verificar_token_rejeita_token_adulterado():
    """
    Simula uma tentativa de adulteração: pega um token válido e
    modifica um caractere da assinatura. A verificação DEVE falhar.
    """
    token = criar_access_token("usuario_teste", "admin")
    token_adulterado = token[:-1] + ("A" if token[-1] != "A" else "B")

    try:
        verificar_token(token_adulterado)
        assert False, "Deveria ter levantado ValueError para token adulterado"
    except ValueError:
        pass  # comportamento esperado
