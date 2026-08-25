# 🗺️ Roadmap de Estudos — Backend, Banco de Dados e APIs

Esse roadmap foi montado com base em tudo que vimos até agora. Ele
segue uma ordem de **dificuldade crescente**, e cada item tem:
- **O que é** (linguagem simples)
- **Por que importa**
- **Termo profissional** (pra você reconhecer quando ouvir de novo)
- **Nível**: 🟢 Fácil / 🟡 Médio / 🔴 Difícil

---

## ✅ O que você já domina (não precisa revisar)

- PostgreSQL: criar banco, tabela, usuário com permissão limitada
- CRUD (Create, Read, Update, Delete) em SQL e em Python
- Conexão seguras com `.env`, variáveis de ambiente
- Transações (`commit`/`rollback`), o "tudo ou nada"
- Modelagem relacional (chave estrangeira, tabelas relacionadas)
- Diferença entre SQL e NoSQL
- API REST: métodos HTTP, JSON, status codes básicos (200, 201, 404, 400)
- Construir uma API do zero (FastAPI)
- Autenticação com JWT e hash de senha (bcrypt)
- Paginação e query strings

Isso já é uma base sólida. Bora pros próximos passos.

---

## 🟢 Nível Fácil — extensão direta do que você já sabe

### 1. `curl` — o "Postman do terminal"
**O que é:** um comando de terminal que manda requisições HTTP, sem precisar abrir nenhum programa gráfico. Como você já usa Postman, é literalmente a mesma coisa, só que digitada.
```bash
curl -X GET http://127.0.0.1:8000/clientes
```
**Por que importa:** em servidores sem tela (a maioria dos servidores reais), não tem Postman nem navegador — só terminal. `curl` é praticamente universal.
**Termo pra guardar:** "requisição via CLI" (CLI = Command Line Interface, interface de linha de comando).

### 2. Script Python simples com `requests`
**O que é:** em vez de clicar em botões no Postman, escrever um `.py` que faz a chamada pra você. Você já viu isso no `consumo_api_publica.py` (chamando a ViaCEP) — agora é só apontar pra **sua própria API**.
**Por que importa:** é o primeiro passo pra automatizar testes, ou pra um programa "de verdade" (não um humano) consumir sua API.
**Termo pra guardar:** "cliente HTTP" (qualquer programa que faz requisições, seja Postman, `curl`, ou um script).

### 3. Docker (parte 1: só rodar, não criar)
**O que é:** uma forma de "empacotar" um programa (como o Postgres) junto com tudo que ele precisa pra rodar, numa caixinha isolada chamada **container**. Em vez de instalar Postgres direto no seu Linux (como fizemos), você roda ele "dentro" do Docker.
**Por que importa:** elimina o "na minha máquina funciona" — todo mundo que usa o mesmo container tem o ambiente idêntico.
**Termo pra guardar:** "container" (não é uma máquina virtual completa, é mais leve — ele compartilha o sistema operacional de baixo, só isola o programa).

---

## 🟡 Nível Médio — os buracos que identificamos na sua API

### 4. Autorização por papel (RBAC)
**O que é:** hoje, todo mundo que loga na sua API pode fazer **qualquer coisa**. RBAC é dar "crachás diferentes" — um usuário "funcionário" só lê, um "admin" pode apagar. Você já tem a base (JWT) pronta pra isso; só falta guardar um campo `papel` (ou `role`) no token e checar ele antes de liberar ações sensíveis.
**Por que importa:** é o item de segurança mais citado em qualquer entrevista técnica sobre API.
**Termo pra guardar:** **RBAC** = Role-Based Access Control (controle de acesso baseado em papel/função).

### 5. HTTPS / TLS
**O que é:** hoje sua API roda em `http://` (sem "s"), ou seja, **sem criptografia** — qualquer um numa mesma rede consegue ler o token JWT passando "pelado". HTTPS embrulha essa conversa numa camada criptografada.
**Por que importa:** sem isso, tudo que fizemos sobre segurança de senha e token vira decorativo, porque o dado trafega exposto de qualquer jeito.
**Termo pra guardar:** **TLS** (Transport Layer Security) é o nome técnico do "motor" por trás do HTTPS — SSL é o nome antigo da mesma ideia, hoje em desuso mas ainda ouvido por aí.

### 6. Expiração e revogação de token
**O que é:** hoje, se um token JWT vazar, ele continua **válido até expirar sozinho** (30 min) — não tem como "cancelar" ele na mão. Existe um padrão chamado **refresh token**: um token de vida curta (pra usar nas requisições) + um token de vida longa (só pra pedir um token novo), que dá mais controle.
**Por que importa:** é o meio-termo entre "token que nunca expira" (perigoso) e "usuário logando a cada 30 min" (chato).
**Termo pra guardar:** **refresh token**, e **revogação de token** (invalidar um token antes da hora).

### 7. CORS
**O que é:** uma regra de segurança que **navegadores** aplicam sozinhos: um site rodando em `meusite.com` não pode, por padrão, chamar uma API rodando em outro endereço (`minhaapi.com`), a não ser que a API **autorize isso explicitamente**.
**Por que importa:** no dia em que você quiser um front-end (site) separado consumindo sua API, você vai bater nesse erro certeza — e sem saber o nome, ele parece um bug misterioso.
**Termo pra guardar:** **CORS** = Cross-Origin Resource Sharing (compartilhamento de recursos entre origens diferentes).

### 8. Rate limiting
**O que é:** limitar quantas requisições uma mesma pessoa/IP pode fazer num período (ex: 100 pedidos por minuto). Impede que alguém sobrecarregue sua API de propósito ou por acidente.
**Por que importa:** é uma defesa contra ataques de força bruta (tentar mil senhas seguidas no `/login`, por exemplo) e contra picos de tráfego.
**Termo pra guardar:** **rate limiting**, e o ataque que ele previne se chama **brute force** (força bruta).

### 9. Testes automatizados
**O que é:** em vez de testar manualmente no `/docs` toda vez, escrever código que **testa seu próprio código** sozinho, e te avisa se algo quebrou.
**Por que importa:** hoje, se você mudar uma linha do `crud.py`, só vai saber se quebrou testando na mão. Com testes automatizados, você roda um comando e sabe em segundos.
**Termo pra guardar:** **pytest** (a ferramenta mais usada em Python), e **teste unitário** (testa uma função isolada) vs **teste de integração** (testa o sistema todo junto, tipo API + banco).

### 10. Docker (parte 2: criar seus próprios containers)
**O que é:** depois de aprender a "rodar" containers prontos (item 3), o próximo passo é escrever um `Dockerfile` — a "receita" de como empacotar a **sua própria API** num container.
**Por que importa:** é assim que profissionais entregam aplicações prontas pra rodar em qualquer lugar, sem "ué, funciona na minha máquina".
**Termo pra guardar:** **Dockerfile**, **imagem** (o "molde" gerado a partir do Dockerfile) vs **container** (uma "instância" rodando dessa imagem).

---

## 🔴 Nível Difícil — aqui começa "system design" de verdade

### 11. Cache
**O que é:** guardar respostas que já foram calculadas/buscadas, numa "memória rápida" separada (geralmente **Redis**), pra não precisar ir no banco de dados toda vez que alguém pedir a mesma coisa.
**Por que importa:** é uma das formas mais eficazes de deixar um sistema rápido em escala grande.
**Termo pra guardar:** **cache hit** (achou no cache, não precisou ir no banco) vs **cache miss** (não achou, foi buscar de verdade), e **cache invalidation** (o desafio de saber quando um dado em cache ficou "velho" e precisa ser atualizado — famoso por ser considerado um dos problemas mais difíceis da computação).

### 12. Escalabilidade de banco de dados
**O que é:** técnicas pra um banco aguentar **muito mais gente** mexendo ao mesmo tempo:
- **Réplica de leitura** (read replica): cópias do banco só para leitura, aliviando o banco principal
- **Sharding**: dividir os dados em pedaços, cada um guardado em um servidor diferente
**Por que importa:** é literalmente o assunto central de qualquer entrevista de "system design" envolvendo dados.
**Termo pra guardar:** **replication** (replicação), **sharding**, **horizontal scaling** (adicionar mais máquinas) vs **vertical scaling** (deixar uma máquina só mais forte).

### 13. Balanceamento de carga
**O que é:** quando você tem **várias cópias** da sua API rodando (não só uma), um "load balancer" distribui os pedidos entre elas, pra nenhuma ficar sobrecarregada.
**Por que importa:** é o que permite um sistema aguentar milhões de usuários sem que um servidor só "quebre".
**Termo pra guardar:** **load balancer**, e **stateless** (lembra que mencionei antes? uma API sem "memória" de requisição pra requisição é o que torna possível balancear carga facilmente, porque qualquer servidor pode responder qualquer pedido).

### 14. Filas de mensagens
**O que é:** em vez de um pedido esperar uma tarefa demorada terminar na hora (ex: mandar 10 mil e-mails), você "enfileira" a tarefa (numa ferramenta tipo **RabbitMQ** ou **Kafka**) e ela é processada depois, em segundo plano.
**Por que importa:** evita que ações demoradas travem a experiência do usuário.
**Termo pra guardar:** **message queue** (fila de mensagens), **processamento assíncrono** (assíncrono = "não trava esperando").

### 15. CI/CD
**O que é:** automatizar o processo de "testar código novo" (Continuous Integration) e "colocar ele no ar" (Continuous Deployment), sem alguém precisando fazer isso na mão toda vez.
**Por que importa:** é como equipes profissionais lançam atualizações várias vezes por dia sem quebrar tudo.
**Termo pra guardar:** **pipeline** (a sequência automática de passos: testar → construir → publicar).

### 16. Microserviços vs. Monolito
**O que é:** hoje, nosso projeto é um **monolito** — tudo (clientes, pedidos, autenticação) roda junto, num só programa. **Microserviços** é dividir isso em vários programinhas independentes (um só de clientes, um só de pagamento, um só de autenticação), que se comunicam entre si.
**Por que importa:** é uma decisão arquitetural gigante — cada abordagem tem vantagens e desvantagens bem debatidas, e é tema quase certo em entrevista de system design sênior.
**Termo pra guardar:** **monolito**, **microserviços**, e **acoplamento** (o quanto uma parte do sistema depende de outra).

---

## 📌 Sugestão de próximo passo imediato

Dado tudo que já discutimos, eu seguiria **nessa ordem exata**:
1. `curl` (10 minutos, ganho imediato)
2. Script Python com `requests` chamando sua própria API
3. RBAC (autorização por papel) — fecha o buraco de segurança mais falado
4. HTTPS/TLS — mesmo que só conceitual por enquanto (implementar isso local é meio artificial, geralmente é resolvido pela plataforma de nuvem)
5. Docker parte 1

Isso te dá prática real com ferramentas de mercado, fecha os buracos de segurança mais importantes, e prepara o terreno pra falar de escalabilidade com uma base prática por trás — em vez de só decorar os termos do "nível difícil".
