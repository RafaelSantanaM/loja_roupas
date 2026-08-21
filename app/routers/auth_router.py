"""
app/routers/auth_router.py
=============================
Rotas de autenticação (login, refresh, logout), extraídas do antigo
api.py. Um APIRouter agrupa endpoints relacionados sob um prefixo
comum -- aqui, tudo nasce sob /auth (ex: POST /auth/login), em vez
de conviver solto junto com as rotas de clientes no mesmo arquivo.

NOTA: os endpoints continuam usando os módulos antigos (auth, crud,
usuarios_crud, refresh_tokens_crud) exatamente como estavam em
api.py -- só o LOCAL do código mudou, a lógica é idêntica.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

import auth
import usuarios_crud
import refresh_tokens_crud
from app.limiter import limiter
from app.schemas.auth_schemas import RefreshRequest

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """
    POST /auth/login -> devolve access_token (15 min) e refresh_token (7 dias).
    RATE LIMIT: 5/minuto -- alvo primário de brute force.
    """
    usuario = usuarios_crud.buscar_usuario_por_username(form.username)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    usuario_id, username, senha_hash, papel = usuario
    if not auth.conferir_senha(form.password, senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    access_token = auth.criar_access_token(username, papel)
    refresh_token, jti, expira_em = auth.criar_refresh_token(username)
    refresh_tokens_crud.salvar_refresh_token(usuario_id, jti, expira_em)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
@limiter.limit("10/minute")
def refresh(request: Request, dados: RefreshRequest):
    """POST /auth/refresh -> troca um refresh token válido por um access token novo."""
    try:
        payload = auth.verificar_token(dados.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    if payload.get("tipo") != "refresh":
        raise HTTPException(status_code=401, detail="Tipo de token incorreto")

    jti = payload.get("jti")
    if not refresh_tokens_crud.refresh_token_esta_ativo(jti):
        raise HTTPException(status_code=401, detail="Refresh token revogado ou não encontrado")

    username = payload.get("sub")
    usuario = usuarios_crud.buscar_usuario_por_username(username)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    _, _, _, papel = usuario
    novo_access_token = auth.criar_access_token(username, papel)
    return {"access_token": novo_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(dados: RefreshRequest):
    """POST /auth/logout -> revoga um refresh token."""
    try:
        payload = auth.verificar_token(dados.refresh_token)
    except ValueError:
        return {"mensagem": "Logout realizado"}

    jti = payload.get("jti")
    if jti:
        refresh_tokens_crud.revogar_refresh_token(jti)

    return {"mensagem": "Logout realizado"}
