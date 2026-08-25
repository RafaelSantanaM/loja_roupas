# 📚 Documentação Técnica e Guias de Estudo

Bem-vindo à base de conhecimento do projeto **Loja de Roupas API**. Esta pasta reúne os guias conceituais, anotações de engenharia e a evolução cronológica dos estudos aplicados neste sistema.

---

## 🗂️ Índice de Guias

| Arquivo | Tópico Principal | Conceitos Abordados |
|---|---|---|
| [**`01-modelagem-e-transacoes.md`**](./01-modelagem-e-transacoes.md) | Banco de Dados & Transações ACID | PostgreSQL, Foreign Keys, `SELECT FOR UPDATE`, Row-Level Locking, Rollback |
| [**`02-autenticacao-jwt.md`**](./02-autenticacao-jwt.md) | Segurança & Autenticação | Hashing com BCrypt e Salt, JWT (Access Token e Refresh Token), Revogação via JTI |
| [**`03-rbac-autorizacao.md`**](./03-rbac-autorizacao.md) | Controle de Acesso Baseado em Papéis | RBAC, Roles (`admin` vs `funcionario`), Políticas de permissão em rotas |
| [**`04-testes-automatizados.md`**](./04-testes-automatizados.md) | Testes com Pytest | Testes Unitários vs Testes de Integração, Fixtures do Pytest, TestClient |
| [**`05-roadmap-backend.md`**](./05-roadmap-backend.md) | Trilha de Conhecimento Pleno/Sênior | System Design, Cache com Redis, Filas com RabbitMQ, CI/CD Pipelines |

---

## 💡 Exemplos e Scripts Auxiliares

Na pasta [`examples/`](./examples/), você encontra scripts e arquivos utilitários desenvolvidos durante os experimentos de aprendizado:
* **`cliente_api.py`**: Exemplo de cliente HTTP Python consumindo a API com autenticação e paginação.
* **`consumo_api_publica.py`**: Demonstração de integração com APIs públicas externas (ViaCEP).
* **`teste_cors.html`**: Aplicação frontend simples para validação prática de políticas de CORS (*Cross-Origin Resource Sharing*).
* **`certificados/`**: Certificados autoassinados utilizados no laboratório de TLS/HTTPS local.
