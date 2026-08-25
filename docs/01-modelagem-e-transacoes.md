# 🧩 Exercício: Pedidos + Transação de verdade

Este exercício adiciona duas tabelas novas (`produtos` e `pedidos`),
relacionadas com `clientes`, e mostra uma **transação real**
acontecendo — inclusive um `ROLLBACK` de propósito, pra você ver
o "desfazer tudo" com os próprios olhos.

## Como rodar

```bash
# 1) Rode o schema original, se ainda não rodou
psql -U postgres -f schema.sql

# 2) Rode o schema novo, com produtos e pedidos
psql -U postgres -d loja_roupas -f schema_pedidos.sql

# 3) Crie um cliente de teste (se ainda não tiver nenhum)
python main.py

# 4) Rode o exercício de pedidos
python pedidos.py
```

## O que você vai ver acontecer

**Cenário 1 — pedido válido:** pede 1 camiseta (temos 3 em estoque).
O programa:
1. Verifica o preço e o estoque do produto
2. Diminui o estoque em 1
3. Registra o pedido
4. Dá `commit()` — tudo confirmado de vez

**Cenário 2 — pedido inválido:** pede 100 camisetas (só temos 2
sobrando depois do cenário 1). O programa:
1. Verifica o estoque
2. Percebe que não tem o suficiente e **levanta um erro**
   (`EstoqueInsuficiente`)
3. Cai no `except`, chama `conn.rollback()`
4. **Nada** é salvo — nem o estoque muda, nem o pedido é criado

Se você rodar `SELECT * FROM produtos;` depois, vai ver que o
estoque só diminuiu **uma vez** (do pedido válido), mesmo que o
programa tenha "tentado" mexer nele duas vezes.

## Detalhe extra: o `FOR UPDATE`

Repare nessa linha dentro do `criar_pedido`:
```sql
SELECT preco, estoque FROM produtos WHERE id = %s FOR UPDATE;
```

O `FOR UPDATE` "tranca" a fichinha do produto até a transação
terminar (commit ou rollback). Isso evita que **duas pessoas
comprem o último produto ao mesmo tempo** e ambas achem que deu
certo — um problema clássico chamado **condição de corrida**
(race condition). Enquanto uma compra está sendo processada, a
outra espera a fila andar antes de checar o estoque.
