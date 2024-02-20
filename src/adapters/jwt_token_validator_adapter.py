from datetime import datetime

import jwt

from core.config import settings
from ports.token_validator_interface import ITokenValidator


class JWTTokenValidatorAdapter(ITokenValidator):
    def validate_reset_password_link_token(self, link: str) -> dict:
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
