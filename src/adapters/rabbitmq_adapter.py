from typing import Callable

import pika
from pika import exceptions

from ports.message_queue_interface import IMessageQueue


class RabbitMQAdapter(IMessageQueue):
    def __init__(self, url: str):
        self._params = pika.URLParameters(url)
        self._connection = None
        self._channel = None

    def ensure_channel(self):
        if not self._connection or self._connection.is_closed:
            self._connection = pika.BlockingConnection(self._params)
        if not self._channel or self._channel.is_closed:
            self._channel = self._connection.channel()

    def create_exchange_if_not_exists(self, exchange_name: str) -> bool:
        self.ensure_channel()
        try:
            self._channel.exchange_declare(
                exchange=exchange_name,
                exchange_type="direct",
            )
            return True
        except pika.exceptions.ChannelClosedByBroker:
            self.ensure_channel()
            return False

    def create_queue_bind_if_not_exists(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str,
    ) -> bool:
        self.ensure_channel()
        try:
            self._channel.queue_bind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key,
            )
            return True
        except pika.exceptions.ChannelClosedByBroker:
            self.ensure_channel()
            return False

    def initialize_queues(self, queue_name: str, exchange_name: str, routing_key: str):
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

        self._channel.queue_declare(queue=queue_name, arguments=arguments, durable=True)
        self.create_exchange_if_not_exists(exchange_name=exchange_name)
        self.create_queue_bind_if_not_exists(
            queue_name=queue_name,
            exchange_name=exchange_name,
            routing_key=routing_key,
        )

    def setup_dlq(self, dlq_name: str, dlx_name: str):
        self._channel.exchange_declare(
            exchange=dlx_name,
            exchange_type="direct",
            durable=True,
        )
        self._channel.queue_declare(queue=dlq_name, durable=True)
        self._channel.queue_bind(
            queue=dlq_name, exchange=dlx_name, routing_key=dlq_name
        )

    def consume_messages(self, queue_name: str, callback: Callable):
        self._channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False,
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self._channel.start_consuming()
