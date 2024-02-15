import os
import sys

from adapters.mongodb_adapter import MongoDBAdapter
from adapters.rabbitmq_adapter import RabbitMQAdapter
from core.config import settings
from services.message_service import MessageService

mongodb_uri = settings.mongodb.url
rabbitmq_url = settings.rabbitmq.url


def main():
    mongodb_adapter = MongoDBAdapter(
        uri=mongodb_uri,
        db_name="user_data",
        collection_name="password_reset_messages",
    )
    rabbitmq_adapter = RabbitMQAdapter(url=rabbitmq_url)

    message_service = MessageService(
        mq_adapter=rabbitmq_adapter,
        db_adapter=mongodb_adapter,
    )
    message_service.start_listening(queue_name="reset-password-queue")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
