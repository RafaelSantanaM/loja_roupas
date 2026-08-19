"""
filas.py
========
Este módulo é o nosso "PRODUCER" (produtor) -- ou seja, o código que
COLOCA mensagens na fila, sem executar a tarefa ele mesmo.

Relembrando a analogia do restaurante:
- Este arquivo é o GARÇOM, que anota o pedido e pendura a comanda.
- Ele NÃO cozinha nada -- só entrega o pedido pra fila e segue em frente.
"""

import json
import pika

# Onde o RabbitMQ está rodando. Igual fizemos com Redis (localhost:6379),
# aqui é localhost:5672 -- a porta "de conversa entre programas" que
# mapeamos no docker run (lembra? -p 5672:5672)
RABBITMQ_HOST = "localhost"

# Nome da fila que vamos usar para o e-mail de boas-vindas.
# Escolher um nome CLARO é importante -- outra pessoa lendo o código
# deve entender o que essa fila faz só pelo nome.
FILA_BOAS_VINDAS = "fila_boas_vindas"


def publicar_boas_vindas(cliente_id: int, nome: str, email: str) -> None:
    """
    Coloca uma mensagem na fila, pedindo para um e-mail de boas-vindas
    ser enviado depois. NÃO envia o e-mail aqui -- só "avisa" que
    precisa ser enviado.
    """
    # 1) Abre a "ligação telefônica" com o RabbitMQ
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))

    # 2) Abre um "canal" dentro dessa ligação -- é por ele que a
    #    conversa de verdade acontece
    canal = conexao.channel()

    # 3) "Declara" a fila -- avisa "essa fila existe, crie se não existir".
    #    durable=True -> se o RabbitMQ reiniciar, não esquece da fila.
    canal.queue_declare(queue=FILA_BOAS_VINDAS, durable=True)

    # 4) Monta a mensagem. RabbitMQ não entende "dicionário Python"
    #    diretamente -- só entende texto puro (bytes). Por isso
    #    convertemos nosso dicionário para uma STRING no formato JSON
    #    (o mesmo formato que já usamos em toda a nossa API!)
    corpo_da_mensagem = json.dumps({
        "cliente_id": cliente_id,
        "nome": nome,
        "email": email,
    })

    # 5) PUBLICA a mensagem na fila -- este é o momento em que a
    #    "comanda" é pendurada, de fato.
    canal.basic_publish(
        exchange="",                    # "" = envio direto pra fila (sem roteamento extra, o caso mais simples)
        routing_key=FILA_BOAS_VINDAS,   # para QUAL fila estamos mandando
        body=corpo_da_mensagem,
        properties=pika.BasicProperties(
            delivery_mode=2,  # 2 = "mensagem persistente": sobrevive a um reinício do RabbitMQ
        ),
    )

    # 6) Fecha a conexão -- assim como fechamos conexão com o Postgres
    #    depois de usar, fazemos o mesmo aqui, para não deixar recursos abertos à toa
    conexao.close()
