import json

from pika.spec import BasicProperties
from pydantic import ValidationError

from models.reset_password_message_schema import ResetPasswordMessageSchema


class MessageService:
    def __init__(self, mq_adapter, db_adapter, ses_adapter, token_validator_adapter):
        self.mq_adapter = mq_adapter
        self.db_adapter = db_adapter
        self.ses_adapter = ses_adapter
        self.token_validator_adapter = token_validator_adapter

    def parse_message_body(self, body):
        try:
            return json.loads(body) if isinstance(body, bytes) else body
        except json.JSONDecodeError:
            return {}

    def validate_message_and_parse_to_dict(self, message_data) -> dict:
        try:
            reset_password_message = ResetPasswordMessageSchema(**message_data)
            print("Message validated successfully.")
            return reset_password_message.dict()
        except ValidationError:
            print("Message validation failed.")

    def message_received_callback(self, ch, method, properties, body):
        print(f"Received message: {body}")
        try:
            with self.db_adapter.transaction() as session:
                message_data = self.parse_message_body(body)
                reset_password_message = self.validate_message_and_parse_to_dict(
                    message_data=message_data
                )

                if not self.token_validator_adapter.validate_message_password_restoration_link(
                    message=reset_password_message
                ):
                    print("Password reset link is invalid or has expired.")
                    raise ValueError("Invalid or expired password reset link.")

                self.db_adapter.save_message(body=body, session=session)
                self.ses_adapter.prepare_and_send_email(
                    message_data=reset_password_message
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except ValueError as e:
            print(f"Processing failed: {e}")
            self.handle_failure(ch, method, properties, body)
        except Exception as e:
            print(f"Exception occurred: {e}")
            self.handle_failure(ch, method, properties, body)

    def handle_failure(self, ch, method, properties, body):
        headers = properties.headers or {}
        failure_count = headers.get("x-retry-count", 0) + 1
        print(
            f"Handling failure, current retry count is: {failure_count - 1}, incrementing to: {failure_count}"
        )

        if failure_count < 5:
            headers["x-retry-count"] = failure_count
            print(f"Republishing with new retry count: {failure_count}")
            ch.basic_publish(
                exchange=method.exchange,
                routing_key=method.routing_key,
                body=body,
                properties=BasicProperties(headers=headers),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("Sending message to DLQ")
            ch.basic_reject(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )

    def start_listening(self, queue_name: str, exchange_name: str, routing_key: str):
        self.mq_adapter.initialize_queues(
            queue_name=queue_name,
            exchange_name=exchange_name,
            routing_key=routing_key,
        )
        self.mq_adapter.consume_messages(queue_name, self.message_received_callback)
