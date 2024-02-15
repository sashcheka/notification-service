class MessageService:
    def __init__(self, mq_adapter, db_adapter):
        self.mq_adapter = mq_adapter
        self.db_adapter = db_adapter

    def save_message_in_db(self, body):
        message_data = body.decode() if isinstance(body, bytes) else body
        self.db_adapter.save_message({"message": message_data})

    def message_received_callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")
        self.save_message_in_db(body)

    def start_listening(self, queue_name):
        self.mq_adapter.initialize_queue(queue_name)
        self.mq_adapter.consume_messages(queue_name, self.message_received_callback)
