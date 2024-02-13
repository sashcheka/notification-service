import os
import sys

from adapters.rabbitmq_adapter import RabbitMQAdapter
from services.message_service import MessageService

url = "amqp://guest:guest@rabbitmq:5672/"
queue_name = "reset-password-queue"


def main():
    mq_adapter = RabbitMQAdapter(url)
    message_service = MessageService(mq_adapter)
    message_service.start_listening(queue_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
