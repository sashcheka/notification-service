import os
import sys

from adapters.aws_ses_adapter import AWSSESAdapter
from adapters.mongodb_adapter import MongoDBAdapter
from adapters.rabbitmq_adapter import RabbitMQAdapter
from core.config import settings
from services.message_service import MessageService

mongodb_uri = settings.mongodb.url
rabbitmq_url = settings.rabbitmq.url

aws_access_key_id = settings.awsses.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.awsses.AWS_SECRET_ACCESS_KEY
region_name = settings.awsses.REGION_NAME
endpoint_url = settings.awsses.endpoint_url


def main():
    rabbitmq_adapter = RabbitMQAdapter(url=rabbitmq_url)

    mongodb_adapter = MongoDBAdapter(
        uri=mongodb_uri,
        db_name="user_data",
        collection_name="password_reset_messages",
    )

    ses_adapter = AWSSESAdapter(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        endpoint_url=endpoint_url,
    )

    message_service = MessageService(
        mq_adapter=rabbitmq_adapter,
        db_adapter=mongodb_adapter,
        ses_adapter=ses_adapter,
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
