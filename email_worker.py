"""
email_worker.py
================
Este é o nosso "CONSUMER" (consumidor) -- o COZINHEIRO da nossa
analogia. Diferente de todo o resto do projeto, este arquivo NÃO
é chamado pela API, e não é uma função que roda uma vez e termina.

Ele é um PROGRAMA QUE FICA RODANDO PARA SEMPRE, escutando a fila,
esperando mensagens aparecerem, e "cozinhando" (processando) cada
uma assim que chega.

Como rodar (em um terminal SEPARADO, que fica aberto o tempo todo):
    python email_worker.py

Para parar: Ctrl+C
"""

import json
import time

import pika

RABBITMQ_HOST = "localhost"
FILA_BOAS_VINDAS = "fila_boas_vindas"


def processar_mensagem(canal, metodo, propriedades, corpo):
    """
    Esta função é chamada AUTOMATICAMENTE pelo pika, toda vez que uma
    mensagem nova chega na fila. É aqui que a tarefa de verdade acontece.

    Os 4 parâmetros (canal, metodo, propriedades, corpo) são um "contrato"
    que o pika exige -- toda função de processamento de mensagem tem
    essa mesma assinatura, mesmo que a gente não use todos eles sempre.
    """
    dados = json.loads(corpo)  # transforma o JSON (texto) de volta em dicionário Python

    print(f"Mensagem recebida: enviar boas-vindas para {dados['nome']} ({dados['email']})")

    # SIMULAÇÃO de um envio de e-mail demorado (na vida real, aqui
    # entraria uma chamada de verdade para um serviço de e-mail, tipo
    # SendGrid, Amazon SES, etc -- isso costuma levar de 1 a alguns
    # segundos, dependendo do serviço).
    print("   Enviando e-mail... (simulando demora de 3 segundos)")
    time.sleep(3)
    print(f"   E-mail de boas-vindas 'enviado' para {dados['email']}!\n")

    # ACK (acknowledgment) = "confirmo que terminei essa tarefa,
    # pode remover ela da fila". SEM isso, o RabbitMQ considera que
    # a mensagem ainda não foi processada -- se o worker cair antes
    # do ack, a mensagem volta para a fila, para ser tentada de novo
    # por outro worker (ou pelo mesmo, quando voltar). Isso é o que
    # dá à fila a capacidade de "tentar de novo em caso de falha",
    # que mencionamos na teoria.
    canal.basic_ack(delivery_tag=metodo.delivery_tag)


def main():
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    canal = conexao.channel()

    # Declaramos a fila aqui TAMBÉM (mesmo nome, mesma configuração
    # "durable" do filas.py) -- isso é proposital: não importa se o
    # producer ou o consumer liga primeiro, cada lado garante que a
    # fila existe antes de tentar usá-la.
    canal.queue_declare(queue=FILA_BOAS_VINDAS, durable=True)

    # prefetch_count=1 -> "não me dê uma mensagem nova enquanto eu não
    # confirmar (ack) a anterior". Evita que um worker fique sobrecarregado
    # recebendo várias mensagens de uma vez só, antes de dar conta da primeira.
    canal.basic_qos(prefetch_count=1)

    # Registra nossa função "processar_mensagem" para ser chamada
    # AUTOMATICAMENTE sempre que uma mensagem chegar nesta fila.
    canal.basic_consume(queue=FILA_BOAS_VINDAS, on_message_callback=processar_mensagem)

    print(f"Worker escutando a fila '{FILA_BOAS_VINDAS}'... (Ctrl+C para parar)")

    # start_consuming() BLOQUEIA o programa aqui para sempre, ficando
    # "escutando" -- é por isso que este arquivo não "termina sozinho",
    # diferente de tudo que rodamos até agora com "python arquivo.py".
    canal.start_consuming()


if __name__ == "__main__":
    main()
