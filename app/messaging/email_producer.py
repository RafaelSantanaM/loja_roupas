"""
app/messaging/email_producer.py
=================================
Produtor (Producer) responsável por publicar mensagens de e-mail na fila do RabbitMQ.
"""

import json
import pika

from app.core.config import settings

FILA_BOAS_VINDAS = "fila_boas_vindas"
FILA_CONFIRMACAO_PEDIDO = "fila_confirmacao_pedido"


def publicar_boas_vindas(cliente_id: int, nome: str, email: str) -> None:
    """Publica um evento na fila para processamento assíncrono do e-mail de boas-vindas."""
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
    canal = conexao.channel()
    canal.queue_declare(queue=FILA_BOAS_VINDAS, durable=True)

    corpo_da_mensagem = json.dumps({
        "tipo": "boas_vindas",
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


def publicar_confirmacao_pedido(
    pedido_id: int,
    cliente_id: int,
    nome_cliente: str,
    email_cliente: str,
    nome_produto: str,
    quantidade: int,
    valor_total: float,
) -> None:
    """Publica evento assíncrono notificando a compra com sucesso para envio de comprovante por e-mail."""
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
    canal = conexao.channel()
    canal.queue_declare(queue=FILA_CONFIRMACAO_PEDIDO, durable=True)

    corpo_da_mensagem = json.dumps({
        "tipo": "confirmacao_pedido",
        "pedido_id": pedido_id,
        "cliente_id": cliente_id,
        "nome_cliente": nome_cliente,
        "email_cliente": email_cliente,
        "nome_produto": nome_produto,
        "quantidade": quantidade,
        "valor_total": valor_total,
    })

    canal.basic_publish(
        exchange="",
        routing_key=FILA_CONFIRMACAO_PEDIDO,
        body=corpo_da_mensagem,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conexao.close()

