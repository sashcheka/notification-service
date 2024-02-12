from adapters.rabbitmq_adapter import RabbitMQAdapter
from core.config import settings
import time


def handle_message(ch, method, properties, body):
    print(f"Received {body}")


def start_message_consumer():
    while True:
        try:
            rabbitmq_adapter = RabbitMQAdapter(settings.rabbitmq.url)
            rabbitmq_adapter.consume_messages("reset-password-queue", handle_message)
        except Exception as e:
            print(f"Error in message consumer: {e}")
            print("Attempting to restart message consumer in 5 seconds...")
            time.sleep(5)
