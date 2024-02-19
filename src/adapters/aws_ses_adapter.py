import boto3
from botocore.exceptions import ClientError

from ports.aws_ses_interface import IAWSSES


class AWSSESAdapter(IAWSSES):
    def __init__(
        self, aws_access_key_id, aws_secret_access_key, region_name, endpoint_url
    ):
        self.ses_client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self.verify_email_address("your-source-email@example.com")

    def verify_email_address(self, email_address):
        try:
            response = self.ses_client.verify_email_identity(EmailAddress=email_address)
            print(f"Email address verified: {email_address}")
        except ClientError as e:
            print(f"Failed to verify email address {email_address}: {e}")

    def create_html_email_body(self, email_body):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
                color: #333;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                color: #444;
            }}
            a, a:visited {{
                color: #1a0dab;
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <h2>Password Reset Request</h2>
            <p>{email_body}</p>
        </div>
        </body>
        </html>
        """
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
            response = self.ses_client.send_email(**send_args)
            message_id = response["MessageId"]
            print(f"Sent email {message_id} from {source} to {destination}")
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise
        else:
            return message_id
