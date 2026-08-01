# 🧸 Cadastro de Clientes da Loja de Roupas — explicado bem fácil

Vamos fingir que o banco de dados é um **armário gigante** guardado
dentro de uma **casa** (o servidor). Este projeto ensina a montar
esse armário, guardar fichinhas de clientes nele, e trancar tudo
direitinho para ninguém bagunçar.

---

## 🗂️ 1. O que tem em cada arquivo

| Arquivo | O que é, em palavras simples |
|---|---|
| `schema.sql` | A "planta" do armário: cria o banco, a gaveta de clientes e uma chavezinha de acesso |
| `.env.example` | Um modelo de "cartão de senha" — copie para `.env` e preencha de verdade |
| `db.py` | O porteiro: só ele sabe como ligar para o banco de dados |
| `crud.py` | As 4 mágicas: criar, ler, atualizar e apagar clientes |
| `main.py` | Um teste, mostrando tudo funcionando junto |
| `requirements.txt` | Lista de "ferramentinhas" (bibliotecas Python) que precisam ser instaladas |

---

## 🏠 2. Como é a implementação do PostgreSQL (o armário)

1. **Instale o PostgreSQL** na sua máquina (ou use um serviço na nuvem, tipo Supabase, Railway, RDS...).
2. Entre como o usuário "dono da casa" (`postgres`) e rode o `schema.sql`:
   ```bash
   psql -U postgres -f schema.sql
   ```
   Isso vai:
   - Criar o banco `loja_roupas` (o armário)
   - Criar a tabela `clientes` (a gaveta)
   - Criar um usuário `app_loja` que só pode mexer nessa gaveta (a chavezinha)

3. Copie o `.env.example` para `.env` e troque a senha:
   ```bash
   cp .env.example .env
   ```

4. Instale as ferramentinhas do Python:
   ```bash
   pip install -r requirements.txt
   ```

5. Rode o teste:
   ```bash
   python main.py
   ```

---

## 🛣️ 3. Caminhos, conexões e "endpoints"

Bancos de dados como o PostgreSQL não têm "endpoints" tipo uma API
(`/clientes`, `/produtos`...). Em vez disso, eles têm uma **string
de conexão**, que é como o **endereço completo da casa**:

```
postgresql://usuario:senha@host:porta/nome_do_banco
```

Explicando cada pedacinho como se fosse um endereço de carta:

- `usuario` e `senha` → quem é você e sua senha para entrar
- `host` → a rua onde a casa fica (ex: `localhost` = sua própria casa, ou um endereço na internet)
- `porta` → o número da campainha (o padrão do Postgres é **5432**)
- `nome_do_banco` → qual cômodo da casa (armário) você quer abrir

No nosso projeto, o `db.py` monta esse "endereço" pra você, lendo
as informações do `.env` — assim ninguém precisa escrever a senha
no meio do código.

> 💡 Diferente de uma API REST, aqui quem "fala" com o Postgres é
> sempre uma biblioteca (no nosso caso, `psycopg2`), que conversa
> usando o protocolo próprio do Postgres, e não HTTP.

---

## 🔒 4. Como isso está seguro (os "cadeados" que usamos)

1. **Senha nunca no código** — fica só no `.env`, que nunca deve ir
   para o GitHub (adicione ele no `.gitignore`).
2. **Usuário com poder limitado** — criamos o `app_loja`, que só
   pode mexer na tabela `clientes`. Ele **não** pode apagar o banco
   inteiro nem criar outros usuários. É como dar uma chave que só
   abre uma gaveta, não a casa toda.
3. **Consultas parametrizadas (`%s`)** — no `crud.py`, nunca colamos
   o texto do usuário direto na pergunta SQL. Isso evita o ataque
   mais famoso em bancos de dados, chamado **SQL Injection**
   (quando alguém escreve um "feitiço" no lugar do nome e engana o
   banco de dados a fazer coisas perigosas).
4. **Conexão criptografada (`sslmode`)** — quando o banco está na
   internet (não na sua própria máquina), usamos `sslmode=require`
   para que a conversa entre o programa e o banco vá "em código
   secreto", e ninguém no meio do caminho consiga espiar.
5. **Timeout de conexão** — se algo travar, o programa desiste
   depois de alguns segundos, em vez de ficar preso pra sempre.
6. **E-mail único (`UNIQUE`)** — o próprio banco impede que dois
   clientes tenham o mesmo e-mail, protegendo a integridade dos dados.

### Outras boas práticas para quando isso crescer de verdade
- Configurar o arquivo `pg_hba.conf` do Postgres para só aceitar
  conexões de IPs/lugares conhecidos (tipo uma "lista de convidados").
- Fazer backups regulares do banco.
- Se um dia guardar senhas de clientes (não é o caso aqui), **nunca**
  guardar a senha em texto puro — sempre usar um "hash" (tipo
  `bcrypt`), que é uma forma de embaralhar a senha sem jeito de
  desembaralhar de volta.
- Trocar a senha do `.env` de tempos em tempos.

---

## 🧠 5. Resumindo com uma historinha

Imagina uma casa (o **servidor**) com um armário dentro (o
**banco de dados**). Dentro do armário tem uma gaveta (a **tabela
clientes**), e dentro dela, várias fichinhas (**cada cliente**).

Para chegar lá, você precisa saber o **endereço da casa** (host +
porta), ter uma **chave** (usuário + senha) que só abre aquela
gaveta específica, e sempre **fechar bem a porta** depois de usar
(conexões fechadas, senhas escondidas, perguntas feitas do jeito
certo). Assim, ninguém de fora consegue bagunçar as fichinhas dos
seus clientes. 🔐
