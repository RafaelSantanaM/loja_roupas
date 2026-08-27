"""
app/workers/email_worker.py
=============================
Consumidor (Consumer/Worker) assíncrono para processamento e envio de e-mails da fila RabbitMQ.

Como rodar (em processo separado ou container dedicado):
    python -m app.workers.email_worker
"""

import json
import time
import pika

from app.core.config import settings

FILA_BOAS_VINDAS = "fila_boas_vindas"
FILA_CONFIRMACAO_PEDIDO = "fila_confirmacao_pedido"


def processar_boas_vindas(canal, metodo, propriedades, corpo):
    """Callback para mensagens da fila de boas-vindas."""
    dados = json.loads(corpo)
    print(f"[Worker] E-mail Boas-Vindas: enviando para {dados['nome']} ({dados['email']})")

    # Simulação de latência de rede/I/O de envio de e-mail (ex: SendGrid, SES)
    time.sleep(2)
    print(f"[Worker] E-mail de boas-vindas enviado com sucesso para {dados['email']}!\n")

    # ACK para confirmar conclusão da tarefa ao broker
    canal.basic_ack(delivery_tag=metodo.delivery_tag)


def processar_confirmacao_pedido(canal, metodo, propriedades, corpo):
    """Callback para mensagens da fila de confirmação de compra."""
    dados = json.loads(corpo)
    print(
        f"[Worker] E-mail Pedido #{dados['pedido_id']}: confirmando compra de {dados['quantidade']}x "
        f"'{dados['nome_produto']}' (R$ {dados['valor_total']:.2f}) para {dados['nome_cliente']} ({dados['email_cliente']})"
    )

    time.sleep(2)
    print(f"[Worker] Comprovante do Pedido #{dados['pedido_id']} enviado com sucesso para {dados['email_cliente']}!\n")

    canal.basic_ack(delivery_tag=metodo.delivery_tag)


def main():
    print(f"[Worker] Conectando ao RabbitMQ em '{settings.rabbitmq_host}'...")
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
    canal = conexao.channel()

    # Declaração das filas
    canal.queue_declare(queue=FILA_BOAS_VINDAS, durable=True)
    canal.queue_declare(queue=FILA_CONFIRMACAO_PEDIDO, durable=True)

    canal.basic_qos(prefetch_count=1)

    # Registro de consumidores em múltiplas filas
    canal.basic_consume(queue=FILA_BOAS_VINDAS, on_message_callback=processar_boas_vindas)
    canal.basic_consume(queue=FILA_CONFIRMACAO_PEDIDO, on_message_callback=processar_confirmacao_pedido)

    print(f"[Worker] Escutando as filas '{FILA_BOAS_VINDAS}' e '{FILA_CONFIRMACAO_PEDIDO}'... (Pressione Ctrl+C para encerrar)")
    canal.start_consuming()


if __name__ == "__main__":
    main()
