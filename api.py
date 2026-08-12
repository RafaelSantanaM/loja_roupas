"""
api.py
======
Nossa primeira API de verdade! Ela não reinventa nada — só "empresta"
as funções que já criamos no crud.py e as deixa acessíveis via HTTP.

Como rodar:
    pip install fastapi uvicorn
    uvicorn api:app --reload

Depois, abra no navegador:
    http://127.0.0.1:8000/docs
(O FastAPI cria essa telinha de testes sozinho, automaticamente!)
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import crud
import usuarios_crud
import refresh_tokens_crud
import auth
import cache

app = FastAPI(title="API - Cadastro de Clientes")

# ---------------------------------------------------------
# RATE LIMITING
# ---------------------------------------------------------
# key_func=get_remote_address -> identifica o "cliente" pelo IP de origem.
#
# ATENÇÃO (limitação documentada, não um descuido):
# 1) O armazenamento aqui é EM MEMÓRIA (padrão da lib). Funciona
#    corretamente com UMA instância da API. Em ambiente com múltiplas
#    instâncias atrás de um load balancer, cada processo teria seu
#    próprio contador isolado -- a solução correta em produção é um
#    backend compartilhado (Redis), configurado via storage_uri=.
# 2) get_remote_address confia no IP de conexão direta. Atrás de um
#    proxy reverso, seria necessário configurar extração segura do
#    X-Forwarded-For, validando que a origem do header é o próprio
#    proxy confiável -- nunca aceitar esse header vindo direto do
#    cliente sem essa validação.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ---------------------------------------------------------
# CORS: quais origens (sites/apps rodando em outro domínio/porta)
# têm permissão de chamar essa API via navegador.
# ---------------------------------------------------------

# Lista "branca" (whitelist) de origens confiáveis. Em produção, isso
# seria o domínio real do seu front-end (ex: "https://minhaloja.com"),
# nunca "*" (que libera geral -- praticamente nunca é o que você quer
# numa API que exige login).
ORIGENS_PERMITIDAS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=True,       # permite enviar/receber cookies e Authorization
    allow_methods=["*"],          # permite todos os métodos (GET, POST, DELETE...)
    allow_headers=["*"],          # permite todos os cabeçalhos (incluindo Authorization)
)

# ---------------------------------------------------------
# AUTENTICAÇÃO (access token + refresh token)
# ---------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class RefreshRequest(BaseModel):
    refresh_token: str


def get_usuario_atual(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependência usada em TODO endpoint que só exige "estar logado".
    Devolve {"username": ..., "papel": ...}.
    """
    try:
        payload = auth.verificar_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    # Um refresh token NUNCA deve ser aceito aqui -- só access token.
    # Isso evita alguém usar o token "de vida longa" pra acessar dados,
    # o que anularia todo o benefício de ter um token de vida curta.
    if payload.get("tipo") != "access":
        raise HTTPException(status_code=401, detail="Tipo de token incorreto")

    return {"username": payload.get("sub"), "papel": payload.get("papel")}


def exigir_admin(usuario: dict = Depends(get_usuario_atual)) -> dict:
    """
    Segunda "trava": além de estar logado, o papel precisa ser 'admin'.
    Repare que esta função DEPENDE da anterior (Depends dentro de Depends) --
    ou seja, primeiro confere o login, DEPOIS confere o papel.
    """
    if usuario["papel"] != "admin":
        # 403 = "autenticado, mas SEM PERMISSÃO" -- diferente de 401!
        raise HTTPException(status_code=403, detail="Ação restrita a administradores")
    return usuario


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """
    POST /login -> recebe username + senha, devolve DOIS tokens:
    - access_token: vida curta (15 min), usado em cada requisição
    - refresh_token: vida longa (7 dias), usado só pra pedir um access token novo

    RATE LIMIT: 5 tentativas por minuto, por IP. Alvo primário de
    ataques de força bruta e credential stuffing -- justifica o limite
    mais agressivo de toda a API.
    """
    usuario = usuarios_crud.buscar_usuario_por_username(form.username)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    usuario_id, username, senha_hash, papel = usuario
    if not auth.conferir_senha(form.password, senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    access_token = auth.criar_access_token(username, papel)
    refresh_token, jti, expira_em = auth.criar_refresh_token(username)

    # Salva o refresh token no banco -- é isso que permite revogar depois
    refresh_tokens_crud.salvar_refresh_token(usuario_id, jti, expira_em)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh")
@limiter.limit("10/minute")
def refresh(request: Request, dados: RefreshRequest):
    """
    POST /refresh -> troca um refresh token válido por um access token novo,
    SEM precisar de usuário/senha de novo.

    RATE LIMIT: 10/minuto -- moderado. Uso legítimo é esporádico (só
    quando o access token expira); rajadas aqui são indício de anomalia.
    """
    try:
        payload = auth.verificar_token(dados.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    if payload.get("tipo") != "refresh":
        raise HTTPException(status_code=401, detail="Tipo de token incorreto")

    jti = payload.get("jti")
    if not refresh_tokens_crud.refresh_token_esta_ativo(jti):
        # Aqui é onde a REVOGAÇÃO realmente é sentida: mesmo que a
        # assinatura do JWT seja válida, se ele não está mais "ativo"
        # no banco, recusamos.
        raise HTTPException(status_code=401, detail="Refresh token revogado ou não encontrado")

    username = payload.get("sub")
    usuario = usuarios_crud.buscar_usuario_por_username(username)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    _, _, _, papel = usuario
    novo_access_token = auth.criar_access_token(username, papel)
    return {"access_token": novo_access_token, "token_type": "bearer"}


@app.post("/logout")
def logout(dados: RefreshRequest):
    """
    POST /logout -> revoga um refresh token, encerrando a "sessão" de
    verdade (o access token que já foi emitido antes ainda funciona até
    expirar sozinho, mas não será mais possível gerar um access token novo).
    """
    try:
        payload = auth.verificar_token(dados.refresh_token)
    except ValueError:
        # Se o token já é inválido, o objetivo (não estar mais logado)
        # já está cumprido -- não precisa dar erro pro usuário.
        return {"mensagem": "Logout realizado"}

    jti = payload.get("jti")
    if jti:
        refresh_tokens_crud.revogar_refresh_token(jti)

    return {"mensagem": "Logout realizado"}


# =========================================================
# "Moldes" dos dados que entram e saem da API (Pydantic).
# Isso garante que ninguém mande um JSON tortinho (ex: nome
# vazio, e-mail sem @, etc) -- a validação acontece sozinha.
# =========================================================

class ClienteEntrada(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    endereco: Optional[str] = None


class ClienteAtualizacao(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None


# =========================================================
# Endpoints (as "portas de entrada" da nossa API)
# =========================================================

@app.get("/")
def raiz():
    """Rota simples só para conferir se a API está no ar."""
    return {"mensagem": "API da loja de roupas está funcionando!"}


@app.get("/clientes")
@limiter.limit("60/minute")
def listar(
    request: Request,
    usuario: dict = Depends(get_usuario_atual),
    pagina: int = Query(1, ge=1, description="Número da página, começando em 1"),
    tamanho_pagina: int = Query(10, ge=1, le=100, description="Quantos clientes por página (máx 100)"),
    nome: Optional[str] = Query(None, description="Filtra clientes cujo nome contenha esse texto"),
):
    """
    GET /clientes -> lista os clientes, com paginação e filtro opcional.

    Exemplos de uso (via query string, direto na URL):
      /clientes                        -> página 1, 10 por página
      /clientes?pagina=2                -> página 2
      /clientes?tamanho_pagina=5         -> 5 clientes por página
      /clientes?nome=maria               -> só clientes com "maria" no nome
      /clientes?pagina=2&tamanho_pagina=5&nome=silva  -> tudo combinado
    """
    offset = (pagina - 1) * tamanho_pagina  # calcula quantos "pular"
    linhas = crud.listar_clientes(limite=tamanho_pagina, offset=offset, nome=nome)
    total = crud.contar_clientes(nome=nome)

    colunas = ["id", "nome", "email", "telefone", "data_nascimento", "endereco", "criado_em"]
    clientes = [dict(zip(colunas, linha)) for linha in linhas]

    return {
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total_de_clientes": total,
        "total_de_paginas": (total + tamanho_pagina - 1) // tamanho_pagina,  # arredonda pra cima
        "clientes": clientes,
    }


@app.get("/clientes/{cliente_id}")
def buscar(cliente_id: int, usuario: dict = Depends(get_usuario_atual)):
    """GET /clientes/5 -> busca um cliente específico (Read), com cache."""
    cliente_cacheado = cache.buscar_cliente_no_cache(cliente_id)
    if cliente_cacheado is not None:
        # CACHE HIT: devolve sem tocar o banco
        return {**cliente_cacheado, "_origem": "cache"}

    linha = crud.buscar_cliente_por_id(cliente_id)
    if linha is None:
        # 404 = "não encontrado", um dos códigos de status HTTP mais usados
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    colunas = ["id", "nome", "email", "telefone", "data_nascimento", "endereco", "criado_em"]
    cliente = dict(zip(colunas, linha))

    # CACHE MISS: buscou no banco, agora grava para a próxima consulta ser um hit
    cache.salvar_cliente_no_cache(cliente_id, cliente)
    return {**cliente, "_origem": "banco"}


@app.post("/clientes", status_code=201)
def criar(cliente: ClienteEntrada, usuario: dict = Depends(get_usuario_atual)):
    """POST /clientes -> cria um cliente novo (Create)."""
    try:
        novo_id = crud.criar_cliente(
            nome=cliente.nome,
            email=cliente.email,
            telefone=cliente.telefone,
            data_nascimento=cliente.data_nascimento,
            endereco=cliente.endereco,
        )
    except Exception as erro:
        # 400 = "pedido malformado" (ex: e-mail já cadastrado)
        raise HTTPException(status_code=400, detail=str(erro))
    return {"id": novo_id, "mensagem": "Cliente criado com sucesso"}


@app.patch("/clientes/{cliente_id}")
def atualizar(cliente_id: int, dados: ClienteAtualizacao, usuario: dict = Depends(get_usuario_atual)):
    """PATCH /clientes/5 -> atualiza só os campos enviados (Update)."""
    linhas_alteradas = crud.atualizar_cliente(
        cliente_id,
        nome=dados.nome,
        telefone=dados.telefone,
        endereco=dados.endereco,
    )
    if linhas_alteradas == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Invalidação ativa: garante que a próxima leitura não sirva dado velho
    cache.invalidar_cliente_no_cache(cliente_id)
    return {"mensagem": "Cliente atualizado com sucesso"}


@app.delete("/clientes/{cliente_id}")
def deletar(cliente_id: int, usuario: dict = Depends(exigir_admin)):
    """DELETE /clientes/5 -> apaga um cliente (Delete). Só ADMIN pode."""
    linhas_apagadas = crud.deletar_cliente(cliente_id)
    if linhas_apagadas == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cache.invalidar_cliente_no_cache(cliente_id)
    return {"mensagem": "Cliente apagado com sucesso"}