import pika
from ports.imessage_consumer_port import IMessageConsumerPort


class RabbitMQAdapter(IMessageConsumerPort):
    def __init__(self, url):
        self.url = url

    def consume_messages(self, queue: str, callback):
        params = pika.URLParameters(self.url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue)

        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

        print(f"[*] Waiting for messages in {queue}. To exit press CTRL+C")
        channel.start_consuming()
