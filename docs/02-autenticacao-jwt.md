# 🔐 Exercício: Autenticação JWT

Agora os endpoints de `clientes` exigem login. Passo a passo pra testar.

## 1. Rodar a tabela de usuários

```bash
sudo -u postgres psql -d loja_roupas < schema_usuarios.sql
```

## 2. Colocar a chave secreta no `.env`

Adicione essa linha no seu `.env` (troque por qualquer texto grande):
```
JWT_SECRET_KEY=uma-frase-bem-grande-e-aleatoria-so-sua
```

## 3. Criar seu primeiro usuário

```bash
python usuarios_crud.py
```
Isso cria um usuário `admin` com senha `senha123` (só para estudo —
numa aplicação real, nunca deixe uma senha "padrão" dessas).

## 4. Rodar a API de novo

```bash
uvicorn api:app --reload
```

## 5. Testar no `/docs`

1. Abra `http://127.0.0.1:8000/docs`
2. Tente `GET /clientes` sem fazer nada antes → deve dar **`401 Unauthorized`**
   (esse é o resultado esperado agora! Antes disso, qualquer um conseguia
   ler os clientes sem provar quem era)
3. Clique no **cadeadinho verde** (🔓) no canto superior direito da página,
   ou vá em `POST /login`
4. Faça login com `username: admin` e `password: senha123`
5. O Swagger guarda o token sozinho depois do login. Tente `GET /clientes`
   de novo → agora deve funcionar normalmente

## 6. Ver o token expirando (opcional, mas educativo)

O token dura 30 minutos (`MINUTOS_PARA_EXPIRAR` no `auth.py`). Se quiser
testar mais rápido, mude esse número pra `1` no `auth.py`, reinicie a API,
logue de novo, espere 1 minuto, e tente um `GET /clientes` — deve voltar
`401` com "Token inválido ou expirado".

## O que mudou de verdade no código

- **`auth.py`** — faz o hash da senha (bcrypt) e cria/confere o token JWT
- **`usuarios_crud.py`** — CRUD simples da tabela de usuários
- **`api.py`** — ganhou `POST /login`, e todo endpoint de `clientes` agora
  exige `Depends(get_usuario_atual)`, que verifica o token antes de deixar
  a requisição passar

## Detalhe de segurança pra guardar

Note que a senha do usuário **nunca** aparece na resposta da API, nem no
`buscar_usuario_por_username` devolvida pro `login` — só o hash circula
internamente no backend, e mesmo esse hash não vai pro cliente.
