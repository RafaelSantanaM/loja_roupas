"""
filas.py
========
O nosso "PRODUCER" -- coloca mensagens na fila do RabbitMQ.

Antes deste commit, RABBITMQ_HOST estava escrito DIRETO no código.
Agora vem de app/core/config.py.
"""

import json
import pika

from app.core.config import settings

FILA_BOAS_VINDAS = "fila_boas_vindas"


def publicar_boas_vindas(cliente_id: int, nome: str, email: str) -> None:
    """Coloca uma mensagem na fila, pedindo o envio do e-mail de boas-vindas depois."""
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
    canal = conexao.channel()
    canal.queue_declare(queue=FILA_BOAS_VINDAS, durable=True)

    corpo_da_mensagem = json.dumps({
        "cliente_id": cliente_id,
        "nome": nome,
        "email": email,
    })

    canal.basic_publish(
        exchange="",
        routing_key=FILA_BOAS_VINDAS,
        body=corpo_da_mensagem,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conexao.close()
