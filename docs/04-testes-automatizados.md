# 🧪 Exercício: Testes Automatizados (pytest)

## Estrutura criada

```
loja-clientes/
├── pytest.ini
└── tests/
    ├── conftest.py              # fixtures compartilhadas
    ├── test_auth_unit.py        # testes UNITÁRIOS (sem banco, sem rede)
    └── test_api_integration.py  # testes de INTEGRAÇÃO (API + Postgres real)
```

## 1. Pré-requisitos

```bash
pip install -r requirements.txt
```

Os testes assumem que **já existem** os usuários `gerente` (admin) e
`vendedor` (funcionario) no banco -- se ainda não rodou, rode:
```bash
python usuarios_crud.py
```

A API **não** precisa estar rodando via `uvicorn` para esses testes --
o `TestClient` conversa diretamente com o código da aplicação em memória.
O Postgres, esse sim, precisa estar no ar (ele é acessado de verdade).

## 2. Rodar a suíte completa

Na raiz do projeto:
```bash
pytest -v
```

A flag `-v` (verbose) lista cada teste individualmente, com seu nome e
resultado (`PASSED`/`FAILED`), em vez de só um resumo consolidado.

## 3. Rodar só os testes unitários (rápido, sem tocar banco)

```bash
pytest tests/test_auth_unit.py -v
```

Repare na **velocidade** -- esses testes devem rodar em uma fração de
segundo, porque não fazem nenhuma chamada de rede ou disco além do
processamento local do bcrypt.

## 4. Rodar um teste específico

```bash
pytest tests/test_api_integration.py::test_funcionario_nao_pode_deletar_cliente -v
```

## 5. Análise crítica de leitura do resultado

Quando um teste falha, o pytest mostra o **diff** entre o esperado e o
obtido. Por exemplo, se `test_listar_clientes_sem_token_retorna_401`
falhasse, você veria algo como:
```
assert 200 == 401
 +  where 200 = <Response [200 OK]>.status_code
```
Isso significa: você esperava `401` (bloqueio), mas a API devolveu `200`
(deixou passar) -- ou seja, seria uma regressão real de segurança sendo
capturada automaticamente, exatamente o valor central de ter essa suíte.

## 6. Por que a fixture `client` desliga o rate limiter

Se você tentasse rodar a suíte com o rate limiter ativo, o teste
`test_fluxo_refresh_token_emite_novo_access_token` e outros que chamam
`/login` mais de uma vez dentro da mesma sessão de testes eventualmente
esbarrariam no limite de 5/minuto, produzindo `429` em vez do resultado
esperado -- um **falso negativo**: o teste falharia não porque a lógica
de negócio está errada, mas porque um controle de infraestrutura não
relacionado interferiu. Testes devem isolar a variável que estão
validando; por isso a fixture desativa o limiter explicitamente,
com o motivo documentado no próprio código.

## 7. O que essa suíte NÃO cobre (limitações honestas)

- **Isolamento de banco**: os testes rodam contra o banco de desenvolvimento
  real, não um banco de teste dedicado e descartável. Ambientes profissionais
  maduros usam um banco separado, frequentemente recriado do zero a cada
  execução (via *fixtures* de schema ou containers Docker efêmeros).
- **Testes de carga/performance**: aqui validamos *correção funcional*,
  não comportamento sob volume (isso seria escopo de ferramentas como
  `locust` ou `k6`, fora do escopo deste exercício).
- **Cobertura de código (coverage)**: não medimos qual percentual do
  código é exercitado pelos testes. A ferramenta `pytest-cov` faria isso
  (`pip install pytest-cov`, depois `pytest --cov=.`) -- mencionado aqui
  como próximo passo natural, não implementado agora para manter o
  escopo gerenciável.
