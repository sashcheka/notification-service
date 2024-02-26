from datetime import datetime

import jwt

from core.config import settings
from ports.token_validator_interface import ITokenValidator


class JWTTokenValidatorAdapter(ITokenValidator):
    def validate_message_password_restoration_link(self, message):
        reset_password_link = message.get("body", "")

        try:
            payload = self.validate_password_restoration_link_token_and_get_payload(
                reset_password_link
            )
            print("Link validated successfully.")
            return payload
        except ValueError as e:
            print(f"Link validation failed. Error message: {e}")
            return None

    def validate_password_restoration_link_token_and_get_payload(
        self, link: str
    ) -> dict:
        token = link.split("/")[-1]

        try:
            payload = self.decode_jwt_token(
                token=token,
            )

            exp = payload.get("exp")
            if exp is None:
                raise ValueError("Invalid token: No expiration claim.")

            expiration_time = datetime.utcfromtimestamp(exp)
            if datetime.utcnow() >= expiration_time:
                raise ValueError("Token has expired.")

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired.")

        except jwt.PyJWTError:
            raise ValueError(f"JWT error.")

        except Exception:
            raise ValueError(f"Token validation error.")

    def decode_jwt_token(
        self,
        token: str,
        public_key: str = settings.jwt.PUBLIC_KEY_PATH.read_text(),
        algorithm: str = settings.jwt.ALGORITHM,
    ) -> dict:
        decoded = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=[algorithm],
        )
        return decoded
