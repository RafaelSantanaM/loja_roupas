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
# 2) JWT (o "crachá" temporário)
# ---------------------------------------------------------

# Chave secreta usada pra "assinar" o token -- SÓ o servidor conhece.
# Em produção, isso viria do .env, nunca escrito direto no código!
CHAVE_SECRETA = os.getenv("JWT_SECRET_KEY", "troque-essa-chave-em-producao")
ALGORITMO = "HS256"
MINUTOS_PARA_EXPIRAR = 30


def criar_token(username: str, papel: str) -> str:
    """Gera um JWT válido por MINUTOS_PARA_EXPIRAR minutos, já carregando o papel do usuário."""
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_PARA_EXPIRAR)
    payload = {
        "sub": username,      # "sub" = subject, ou seja, de quem é esse token
        "papel": papel,       # RBAC: o "crachá" viaja junto com o token
        "exp": expira_em,     # quando ele expira
    }
    return jwt.encode(payload, CHAVE_SECRETA, algorithm=ALGORITMO)


def verificar_token(token: str) -> dict:
    """
    Confere se o token é válido (assinatura correta e não expirado).
    Devolve um dicionário {"username": ..., "papel": ...}, ou levanta um erro.
    """
    try:
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        username = payload.get("sub")
        papel = payload.get("papel")
        if username is None or papel is None:
            raise JWTError("Token incompleto")
        return {"username": username, "papel": papel}
    except JWTError:
        raise ValueError("Token inválido ou expirado")
