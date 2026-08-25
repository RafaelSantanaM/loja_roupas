# 🔑 Exercício: RBAC (autorização por papel)

## O que mudou no código

- **`usuarios`** ganhou a coluna `papel` (`admin` ou `funcionario`)
- **O token JWT** agora carrega o papel dentro dele (`{"sub": "...", "papel": "...", "exp": ...}`)
- **`get_usuario_atual`** — trava 1: "está logado?" (401 se não)
- **`exigir_admin`** — trava 2, que **depende da trava 1**: "além de logado, é admin?" (403 se não)
- **`DELETE /clientes/{id}`** agora exige `exigir_admin` — só admin apaga cliente
- `GET`, `POST`, `PATCH` continuam liberados pra qualquer usuário logado (admin ou funcionário)

## 401 vs 403 — não confunda!

- **401 Unauthorized** = "eu não sei quem você é" (sem token, token inválido/expirado)
- **403 Forbidden** = "eu sei quem você é, mas você não tem permissão pra isso"

É a diferença entre um segurança de balada que não te deixa nem mostrar o documento (401),
e um segurança que já viu seu documento, sabe seu nome, mas te barra porque a área é só
pra sócios (403).

## Passo a passo pra testar

### 1. Rodar a migração no banco

```bash
sudo -u postgres psql -d loja_roupas < migracao_rbac.sql
```

### 2. Criar um segundo usuário (funcionário comum)

O `usuarios_crud.py` foi atualizado pra criar dois usuários de uma vez
(`gerente`/admin e `vendedor`/funcionario). Rode:

```bash
python usuarios_crud.py
```

> ⚠️ Se der erro de "username já existe" pro `admin` antigo, tudo bem —
> a migração já promoveu ele pra admin. O importante aqui é o `vendedor`
> ser criado como `funcionario`.

### 3. Reiniciar a API

```bash
uvicorn api:app --reload
```

### 4. Testar com o `curl` (ótima forma de fixar o que aprendemos!)

**Login como funcionário comum:**
```bash
TOKEN_FUNC=$(curl -s -X POST http://127.0.0.1:8000/login \
  -d "username=vendedor&password=senha123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

**Tentar apagar um cliente sendo funcionário (deve dar 403):**
```bash
curl -i -X DELETE http://127.0.0.1:8000/clientes/1 \
  -H "Authorization: Bearer $TOKEN_FUNC"
```
*(o `-i` mostra os cabeçalhos da resposta, incluindo o código de status)*

Deve aparecer `HTTP/1.1 403 Forbidden` e `{"detail":"Ação restrita a administradores"}`.

**Agora logando como admin (`gerente`) e tentando de novo:**
```bash
TOKEN_ADMIN=$(curl -s -X POST http://127.0.0.1:8000/login \
  -d "username=gerente&password=senha123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -i -X DELETE http://127.0.0.1:8000/clientes/1 \
  -H "Authorization: Bearer $TOKEN_ADMIN"
```
Agora deve dar certo (`200`), supondo que exista um cliente com id 1.

**Conferir que o funcionário ainda consegue LISTAR normalmente:**
```bash
curl http://127.0.0.1:8000/clientes -H "Authorization: Bearer $TOKEN_FUNC"
```
Deve funcionar normal — RBAC só bloqueia o que foi explicitamente restringido.

## O que observar de verdade nesse teste

O ponto central do exercício é: **o mesmo endpoint, o mesmo código, reage diferente
dependendo de quem está pedindo.** Isso é RBAC funcionando -- a decisão não está mais
em "quem é essa pessoa", está em "qual crachá ela carrega".
