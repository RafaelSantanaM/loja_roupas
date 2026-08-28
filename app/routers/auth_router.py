"""
app/routers/auth_router.py
=============================
Rotas de autenticação (login, refresh, logout).

Neste commit, o import muda de "import auth" para
"from app.core import security", e todas as chamadas "auth.xxx(...)"
viram "security.xxx(...)".
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.repositories import usuario_repo, refresh_token_repo
from app.limiter import limiter
from app.schemas.auth_schemas import RefreshRequest

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """
    POST /auth/login -> devolve access_token (15 min) e refresh_token (7 dias).
    RATE LIMIT: 5/minuto -- alvo primário de brute force.
    PROTEÇÃO: Mitigação contra Timing Attack (User Enumeration) via dummy bcrypt verify.
    """
    usuario = usuario_repo.buscar_usuario_por_username(form.username)
    if usuario is None:
        # Executa verificação fictícia para manter o tempo de resposta em ~150-250ms
        security.conferir_senha(form.password, security.DUMMY_BCRYPT_HASH)
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    usuario_id, username, senha_hash, papel = usuario
    if not security.conferir_senha(form.password, senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    access_token = security.criar_access_token(username, papel)
    refresh_token, jti, expira_em = security.criar_refresh_token(username)
    refresh_token_repo.salvar_refresh_token(usuario_id, jti, expira_em)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
@limiter.limit("10/minute")
def refresh(request: Request, dados: RefreshRequest):
    """
    POST /auth/refresh -> troca um refresh token válido por um novo par (Refresh Token Rotation).
    O token anterior é imediatamente revogado para evitar ataques de repetição (Token Replay Attacks).
    """
    try:
        payload = security.verificar_token(dados.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    if payload.get("tipo") != "refresh":
        raise HTTPException(status_code=401, detail="Tipo de token incorreto")

    jti = payload.get("jti")
    if not refresh_token_repo.refresh_token_esta_ativo(jti):
        raise HTTPException(status_code=401, detail="Refresh token revogado ou não encontrado")

    username = payload.get("sub")
    usuario = usuario_repo.buscar_usuario_por_username(username)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    usuario_id, _, _, papel = usuario

    # 1. Revoga o token atual (princípio de uso único por ciclo)
    refresh_token_repo.revogar_refresh_token(jti)

    # 2. Emite novo access_token e novo refresh_token
    novo_access_token = security.criar_access_token(username, papel)
    novo_refresh_token, novo_jti, novo_expira_em = security.criar_refresh_token(username)
    refresh_token_repo.salvar_refresh_token(usuario_id, novo_jti, novo_expira_em)

    return {
        "access_token": novo_access_token,
        "refresh_token": novo_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
@limiter.limit("15/minute")
def logout(request: Request, dados: RefreshRequest):
    """POST /auth/logout -> revoga um refresh token."""
    try:
        payload = security.verificar_token(dados.refresh_token)
    except ValueError:
        return {"mensagem": "Logout realizado"}

    jti = payload.get("jti")
    if jti:
        refresh_token_repo.revogar_refresh_token(jti)

    return {"mensagem": "Logout realizado"}

