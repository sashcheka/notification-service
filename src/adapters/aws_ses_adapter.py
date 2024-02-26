import boto3
from botocore.exceptions import ClientError

from ports.aws_ses_interface import IAWSSES


class AWSSESAdapter(IAWSSES):
    def __init__(
        self, aws_access_key_id, aws_secret_access_key, region_name, endpoint_url
    ):
        self._ses_client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self._email_address = "your-source-email@example.com"

    def verify_email_address(self):
        try:
            response = self._ses_client.verify_email_identity(
                EmailAddress=self._email_address
            )
            print(f"Email address verified: {self._email_address}")
        except ClientError:
            print(f"Failed to verify email address {self._email_address}.")
            raise

    def create_html_email_body(self, email_body):
        template_path = "src/core/templates/password_reset_template.html"

        with open(template_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        html_content = html_content.replace("{email_body}", email_body)

        return html_content

    def send_email(self, source, destination, subject, text, html, reply_tos=None):
        send_args = {
            "Source": source,
            "Destination": {
                "ToAddresses": (
                    destination if isinstance(destination, list) else [destination]
                )
            },
            "Message": {
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
            },
        }
        if reply_tos:
            send_args["ReplyToAddresses"] = (
                reply_tos if isinstance(reply_tos, list) else [reply_tos]
            )

        try:
            response = self._ses_client.send_email(**send_args)
            message_id = response["MessageId"]
            print(f"Sent email {message_id} from {source} to {destination}")
        except ClientError:
            print(f"Failed to send an email on address: {destination}.")
            raise
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise
        else:
            return message_id

    def prepare_and_send_email(self, message_data):
        try:
            if not all(key in message_data for key in ["email", "subject", "body"]):
                return

            source_email = self._email_address
            destination_email = message_data["email"]
            email_subject = message_data["subject"]
            email_body_text = message_data["body"]
            email_body_html = self.create_html_email_body(email_body_text)

            self.send_email(
                source=source_email,
                destination=destination_email,
                subject=email_subject,
                text=email_body_text,
                html=email_body_html,
            )
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise
