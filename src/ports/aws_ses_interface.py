from abc import ABC, abstractmethod


class IAWSSES(ABC):
    @abstractmethod
    def create_html_email_body(self, email_body):
        pass

    @abstractmethod
    def send_email(self, source, destination, subject, text, html, reply_tos=None):
        pass

    @abstractmethod
    def prepare_and_send_email(self, message_data):
        pass
