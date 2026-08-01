"""
auth.py
=======
Aqui moram as duas partes da autenticação:

1) HASH DE SENHA (bcrypt) -- pra nunca guardar senha em texto puro
2) JWT (JSON Web Token) -- o "crachá temporário" que o usuário
   carrega depois de logar

Analogia geral: fazer login é como entrar num prédio. Você mostra
seu documento na portaria (usuário + senha) UMA VEZ, e ganha um
CRACHÁ (o token) que te deixa entrar nas salas (endpoints) sem
precisar mostrar o documento de novo a cada porta -- só que esse
crachá expira sozinho depois de um tempo.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt, JWTError

# ---------------------------------------------------------
# 1) HASH DE SENHA
# ---------------------------------------------------------

# "bcrypt" é o algoritmo de hash escolhido -- padrão de mercado
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha_pura: str) -> str:
    """Transforma a senha digitada num hash irreversível."""
    return pwd_context.hash(senha_pura)


def conferir_senha(senha_pura: str, hash_salvo: str) -> bool:
    """
    Confere se a senha digitada "bate" com o hash salvo no banco.
    Não existe 'descriptografar' aqui -- o que acontece é: pega a
    senha digitada, passa pelo mesmo processo de hash, e compara
    os dois resultados.
    """
    return pwd_context.verify(senha_pura, hash_salvo)


# ---------------------------------------------------------
# 2) TOKENS: access token (curto) + refresh token (longo)
# ---------------------------------------------------------

CHAVE_SECRETA = os.getenv("JWT_SECRET_KEY", "troque-essa-chave-em-producao")
ALGORITMO = "HS256"

# Access token: curto de propósito -- é o que viaja em CADA requisição
MINUTOS_ACCESS_TOKEN = 15

# Refresh token: longo -- só é usado pra pedir um access token novo
DIAS_REFRESH_TOKEN = 7


def criar_access_token(username: str, papel: str) -> str:
    """Gera o token de acesso, de vida curta, usado em cada requisição."""
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_ACCESS_TOKEN)
    payload = {
        "sub": username,
        "papel": papel,
        "tipo": "access",
        "exp": expira_em,
    }
    return jwt.encode(payload, CHAVE_SECRETA, algorithm=ALGORITMO)


def criar_refresh_token(username: str) -> tuple[str, str, datetime]:
    """
    Gera o token de renovação, de vida longa.
    Devolve (token, jti, data_de_expiracao) -- o "jti" e a data de
    expiração são o que vamos SALVAR NO BANCO, pra poder revogar depois.
    """
    jti = str(uuid.uuid4())  # um "número de série" único pra esse token
    expira_em = datetime.now(timezone.utc) + timedelta(days=DIAS_REFRESH_TOKEN)
    payload = {
        "sub": username,
        "tipo": "refresh",
        "jti": jti,
        "exp": expira_em,
    }
    token = jwt.encode(payload, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token, jti, expira_em


def verificar_token(token: str) -> dict:
    """
    Confere assinatura e validade de QUALQUER um dos dois tipos de token.
    Devolve o payload inteiro decodificado, ou levanta um erro.
    """
    try:
        return jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
    except JWTError:
        raise ValueError("Token inválido ou expirado")