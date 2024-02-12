from adapters.rabbitmq_adapter import RabbitMQAdapter
from core.config import settings


def handle_message(ch, method, properties, body):
    print(f"Received {body}")


def start_message_consumer():
    rabbitmq_adapter = RabbitMQAdapter(settings.rabbitmq.url)
    rabbitmq_adapter.consume_messages("reset-password-queue", handle_message)
