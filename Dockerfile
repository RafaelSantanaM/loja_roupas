# =========================================================
# Dockerfile
# Receita de como "empacotar" a nossa API numa imagem Docker.
# =========================================================

# 1) Imagem-base: Python 3.12, variante "slim" (sistema mínimo,
#    sem ferramentas gráficas ou pacotes desnecessários -- imagem
#    final bem menor que a imagem "completa" do Python).
FROM python:3.12-slim

# 2) Diretório de trabalho DENTRO do container. Todo comando
#    seguinte (COPY, RUN, CMD) roda relativo a esse caminho.
WORKDIR /app

# 3) Dependências de SISTEMA necessárias para compilar psycopg2
#    (a biblioteca de conexão com Postgres precisa de libpq).
#    --no-install-recommends evita pacotes "sugeridos" desnecessários,
#    mantendo a imagem enxuta. Limpamos o cache do apt na mesma
#    camada, para não deixar lixo ocupando espaço na imagem final.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 4) CACHE STRATEGY: copiamos APENAS o requirements.txt primeiro.
#    Enquanto esse arquivo não mudar, o Docker reutiliza o cache
#    desta camada em builds futuras, pulando a reinstalação inteira
#    -- mesmo que o código da aplicação (api.py, crud.py...) mude.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) SÓ AGORA copiamos o resto do código -- essa camada muda com
#    frequência (a cada alteração de código), mas isso não afeta
#    a camada de dependências acima, que permanece em cache.
COPY . .

# 6) SEGURANÇA (Princípio do Menor Privilégio):
#    Cria um usuário não-root para execução da aplicação, impedindo que
#    possíveis explorações obtenham acesso de superusuário ao container/host.
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# 7) Documentação da porta usada (não abre a porta sozinho --
#    isso é feito depois, no "docker run -p" ou no docker-compose).
EXPOSE 8000

# 8) Comando executado quando o container INICIA.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

