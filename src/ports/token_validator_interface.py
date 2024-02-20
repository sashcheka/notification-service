from abc import ABC, abstractmethod


class ITokenValidator(ABC):
    @abstractmethod
    def validate_reset_password_link_token(self, link: str) -> dict:
        pass

    @abstractmethod
    def decode_jwt_token(self, token: str, public_key: str, algorithm: str) -> dict:
        pass
