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


def processar_mensagem(canal, metodo, propriedades, corpo):
    """Callback invocado automaticamente pelo RabbitMQ a cada nova mensagem recebida."""
    dados = json.loads(corpo)

    print(f"[Worker] Mensagem recebida: enviando boas-vindas para {dados['nome']} ({dados['email']})")

    # Simulação de latência de rede/I/O de envio de e-mail (ex: SendGrid, SES)
    time.sleep(3)
    print(f"[Worker] E-mail de boas-vindas enviado com sucesso para {dados['email']}!\n")

    # ACK (Acknowledgment) para confirmar conclusão da tarefa ao broker
    canal.basic_ack(delivery_tag=metodo.delivery_tag)


def main():
    print(f"[Worker] Conectando ao RabbitMQ em '{settings.rabbitmq_host}'...")
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
    canal = conexao.channel()

    canal.queue_declare(queue=FILA_BOAS_VINDAS, durable=True)
    canal.basic_qos(prefetch_count=1)
    canal.basic_consume(queue=FILA_BOAS_VINDAS, on_message_callback=processar_mensagem)

    print(f"[Worker] Escutando a fila '{FILA_BOAS_VINDAS}'... (Pressione Ctrl+C para encerrar)")
    canal.start_consuming()


if __name__ == "__main__":
    main()
