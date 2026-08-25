"""
app/messaging/email_producer.py
=================================
Produtor (Producer) responsável por publicar mensagens de e-mail na fila do RabbitMQ.
"""

import json
import pika

from app.core.config import settings

FILA_BOAS_VINDAS = "fila_boas_vindas"


def publicar_boas_vindas(cliente_id: int, nome: str, email: str) -> None:
    """Publica um evento na fila para processamento assíncrono do e-mail de boas-vindas."""
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
