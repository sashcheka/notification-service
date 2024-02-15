from typing import Callable

import pika

from ports.message_queue_interface import IMessageQueue


class RabbitMQAdapter(IMessageQueue):
    def __init__(self, url: str):
        self.params = pika.URLParameters(url)
        self.connection = None
        self.channel = None

    def initialize_queue(self, queue_name: str):
        if not self.connection or not self.channel:
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name)

    def consume_messages(self, queue_name: str, callback: Callable):
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True,
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()
