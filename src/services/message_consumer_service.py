from adapters.rabbitmq_adapter import setup_rabbitmq_consumer
from adapters.mongodb_adapter import MongoDBAdapter


def callback(ch, method, properties, body):
    message = body.decode()
    print(f"Received: {message}")

    import json

    message_dict = json.loads(message)

    mongo_adapter.insert_message(message_dict)


mongo_adapter = MongoDBAdapter("mongodb://mongo:mongo@localhost:27017/")


def start_service():
    setup_rabbitmq_consumer("your_queue_name", callback)
