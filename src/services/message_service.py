import json

from pydantic import ValidationError

from models.reset_password_message_schema import ResetPasswordMessageSchema


class MessageService:
    def __init__(self, mq_adapter, db_adapter, ses_adapter):
        self.mq_adapter = mq_adapter
        self.db_adapter = db_adapter
        self.ses_adapter = ses_adapter

    def save_message_in_db(self, body):
        message_data = body.decode() if isinstance(body, bytes) else body
        self.db_adapter.save_message({"message": message_data})

    def send_email(self, source, destination, subject, text, html, reply_tos=None):
        self.ses_adapter.send_email(source, destination, subject, text, html, reply_tos)

    def parse_message_body(self, body):
        try:
            return json.loads(body) if isinstance(body, bytes) else body
        except json.JSONDecodeError:
            return {}

    def prepare_and_send_email(self, message_data):
        if not all(key in message_data for key in ["email", "subject", "body"]):
            return

        source_email = "your-source-email@example.com"
        destination_email = message_data["email"]
        email_subject = message_data["subject"]
        email_body_text = message_data["body"]
        email_body_html = self.ses_adapter.create_html_email_body(email_body_text)

        self.send_email(
            source=source_email,
            destination=destination_email,
            subject=email_subject,
            text=email_body_text,
            html=email_body_html,
        )

    def validate_message_password_restoration_link(self, message):
        pass

    def validate_message(self, message_data):
        try:
            reset_password_message = ResetPasswordMessageSchema(**message_data)
            print("Message validated successfully.")
            return reset_password_message
        except ValidationError:
            print("Message validation failed.")

    def message_received_callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")
        try:
            message_data = self.parse_message_body(body)
            reset_password_message = self.validate_message(message_data)

            self.save_message_in_db(body)
            self.prepare_and_send_email(reset_password_message.dict())
        except ValidationError:
            print("The message received is not valid and will not be processed.")

    def start_listening(self, queue_name):
        self.mq_adapter.initialize_queue(queue_name)
        self.mq_adapter.consume_messages(queue_name, self.message_received_callback)
