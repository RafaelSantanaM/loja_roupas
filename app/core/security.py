"""
app/core/security.py
======================
Hash de senha (bcrypt) e emissão/verificação de JWT.

Antes deste commit, este arquivo era auth.py, solto na raiz do
projeto. Foi renomeado para "security.py" (convenção comum em
projetos FastAPI reais) e movido para dentro de app/core/, junto
com as outras preocupações transversais (config, cache) -- ou seja,
coisas usadas por múltiplos domínios (autenticação, clientes),
não pertencentes a um único domínio específico.

O CONTEÚDO não mudou -- só o endereço.
"""

import uuid
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt, JWTError

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha_pura: str) -> str:
    """Transforma a senha digitada num hash irreversível."""
    return pwd_context.hash(senha_pura)


def conferir_senha(senha_pura: str, hash_salvo: str) -> bool:
    """Confere se a senha digitada 'bate' com o hash salvo no banco."""
    return pwd_context.verify(senha_pura, hash_salvo)


def criar_access_token(username: str, papel: str) -> str:
    """Gera o token de acesso, de vida curta, usado em cada requisição."""
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.minutos_access_token)
    payload = {
        "sub": username,
        "papel": papel,
        "tipo": "access",
        "exp": expira_em,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algoritmo)


def criar_refresh_token(username: str) -> tuple[str, str, datetime]:
    """Gera o token de renovação, de vida longa. Devolve (token, jti, data_de_expiracao)."""
    jti = str(uuid.uuid4())
    expira_em = datetime.now(timezone.utc) + timedelta(days=settings.dias_refresh_token)
    payload = {
        "sub": username,
        "tipo": "refresh",
        "jti": jti,
        "exp": expira_em,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algoritmo)
    return token, jti, expira_em


def verificar_token(token: str) -> dict:
    """Confere assinatura e validade de qualquer um dos dois tipos de token."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algoritmo])
    except JWTError:
        raise ValueError("Token inválido ou expirado")
