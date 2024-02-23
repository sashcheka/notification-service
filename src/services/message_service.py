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

    def validate_message_password_restoration_link(self, message):
        reset_password_link = message.get("body", "")

        try:
            payload = self.token_validator_adapter.validate_reset_password_link_token(
                reset_password_link
            )
            print("Link validated successfully.")
            return payload
        except ValueError as e:
            print(f"Link validation failed. Error message: {e}")
            return None

    def validate_message_and_parse_to_dict(self, message_data):
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

                if not self.validate_message_password_restoration_link(
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
        failure_count = properties.headers["x-retry-count"] + 1
        print(
            f"Handling failure, current retry count is: {failure_count - 1}, incrementing to: {failure_count}"
        )

        if failure_count < 5:
            headers = properties.headers or {}
            headers["x-retry-count"] = failure_count
            print(f"Republishing with new retry count: {failure_count}")
            ch.basic_publish(
                exchange=method.exchange,
                routing_key=method.routing_key,
                body=body,
                properties=BasicProperties(headers=headers),
            )
        else:
            print("Sending message to DLQ")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_listening(self, queue_name):
        self.mq_adapter.initialize_queue(queue_name)
        self.mq_adapter.consume_messages(queue_name, self.message_received_callback)
