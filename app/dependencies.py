"""
app/dependencies.py
=====================
As "travas" de autenticação (get_usuario_atual) e autorização
(exigir_admin).

Neste commit, o import muda de "import auth" (módulo antigo, na
raiz) para "from app.core import security" (novo endereço) -- e
as chamadas de "auth.verificar_token(...)" viram
"security.verificar_token(...)".
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core import security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_usuario_atual(token: str = Depends(oauth2_scheme)) -> dict:
    """Trava 1: exige um access token válido."""
    try:
        payload = security.verificar_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    if payload.get("tipo") != "access":
        raise HTTPException(status_code=401, detail="Tipo de token incorreto")

    return {"username": payload.get("sub"), "papel": payload.get("papel")}


def exigir_admin(usuario: dict = Depends(get_usuario_atual)) -> dict:
    """Trava 2: além de logado, exige papel 'admin'."""
    if usuario["papel"] != "admin":
        raise HTTPException(status_code=403, detail="Ação restrita a administradores")
    return usuario
