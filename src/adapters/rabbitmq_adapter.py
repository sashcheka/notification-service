from typing import Callable

import pika

from ports.message_queue_interface import IMessageQueue


class RabbitMQAdapter(IMessageQueue):
    def __init__(self, url: str):
        self.params = pika.URLParameters(url)
        self.connection = None
        self.channel = None

    def ensure_channel(self):
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.params)
        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()

    def initialize_queue(self, queue_name: str):
        dlq_name = "reset-password-queue-dlq"
        dlx_name = "reset-password-queue-dlx"

        self.ensure_channel()
        self.setup_dlq(dlq_name, dlx_name)

        arguments = {
            "x-dead-letter-exchange": dlx_name,
            "x-dead-letter-routing-key": dlq_name,
            "x-message-ttl": 60000,
            "x-max-length": 10000,
        }
        self.channel.queue_declare(queue=queue_name, arguments=arguments, durable=True)

    def setup_dlq(self, dlq_name: str, dlx_name: str):
        self.ensure_channel()
        self.channel.exchange_declare(
            exchange=dlx_name,
            exchange_type="direct",
            durable=True,
        )
        self.channel.queue_declare(queue=dlq_name, durable=True)
        self.channel.queue_bind(queue=dlq_name, exchange=dlx_name, routing_key=dlq_name)

    def consume_messages(self, queue_name: str, callback: Callable):
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False,
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def publish_to_dlq(self, dlq_name: str, body):
        self.ensure_channel()
        self.channel.basic_publish(exchange="", routing_key=dlq_name, body=body)
