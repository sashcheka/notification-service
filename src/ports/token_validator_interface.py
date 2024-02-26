from abc import ABC, abstractmethod


class ITokenValidator(ABC):
    @abstractmethod
    def validate_message_password_restoration_link(self, message: dict):
        pass

    @abstractmethod
    def validate_password_restoration_link_token_and_get_payload(
        self, link: str
    ) -> dict:
        pass

    @abstractmethod
    def decode_jwt_token(self, token: str, public_key: str, algorithm: str) -> dict:
        pass
