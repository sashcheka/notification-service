class MessageService:
    def __init__(self, mq_adapter):
        self.mq_adapter = mq_adapter

    def message_received_callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")

    def start_listening(self, queue_name):
        self.mq_adapter.initialize_queue(queue_name)
        self.mq_adapter.consume_messages(queue_name, self.message_received_callback)
