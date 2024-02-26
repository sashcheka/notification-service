import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest

from adapters.jwt_token_validator_adapter import JWTTokenValidatorAdapter
from core.config import settings
from services.message_service import MessageService


@pytest.fixture
def message_data():
    return {
        "id": "f6050865-dd60-4f03-8ef8-cba1ba172bf9",
        "user_id": "76094a14-8ec4-485f-8a77-df1ba194281a",
        "email": "user@example.com",
        "subject": "Reset your password",
        "body": "Link to reset your password: http://example.com/reset",
        "published_at": "2024-02-23T15:57:08.057476",
        "sent_at": "2024-02-23T15:57:08.098342",
    }


@pytest.fixture
def message_service():
    mq_adapter = Mock()
    db_adapter = Mock()
    ses_adapter = Mock()
    token_validator_adapter = Mock()
    return MessageService(mq_adapter, db_adapter, ses_adapter, token_validator_adapter)


def test_parse_message_body(message_service, message_data):
    body = json.dumps(message_data).encode("utf-8")
    parsed_body = message_service.parse_message_body(body)
    assert (
        parsed_body == message_data
    ), "The message body should be correctly parsed as JSON"


def test_validate_message_and_parse_to_dict(message_service, message_data):
    with patch("services.message_service.ResetPasswordMessageSchema") as mock_schema:
        mock_schema.return_value.dict.return_value = message_data
        result = message_service.validate_message_and_parse_to_dict(message_data)
        mock_schema.assert_called_once_with(**message_data)
        assert (
            result == message_data
        ), "The message should be validated and parsed to dict successfully"


@pytest.fixture
def token_validator_adapter():
    return JWTTokenValidatorAdapter()


def test_valid_token(token_validator_adapter):
    expiration_time = datetime.utcnow() + timedelta(days=1)
    token = generate_valid_token(expiration_time)
    body = f"Link to reset your password: http://localhost:8001/auth/reset-password-check/{token}"

    payload = token_validator_adapter.validate_message_password_restoration_link(
        {"body": body}
    )

    assert payload is not None


def test_invalid_token(token_validator_adapter):
    token = "invalid_token"

    payload = token_validator_adapter.validate_message_password_restoration_link(
        {"body": token}
    )

    assert payload is None


def test_expired_token(token_validator_adapter):
    expiration_time = datetime.utcnow() - timedelta(days=1)
    token = generate_valid_token(expiration_time)

    payload = token_validator_adapter.validate_message_password_restoration_link(
        {"body": token}
    )

    assert payload is None


def generate_valid_token(expiration_time):
    private_key: str = settings.jwt.PRIVATE_KEY_PATH.read_text()
    algorithm: str = settings.jwt.ALGORITHM
    payload = {
        "exp": expiration_time.timestamp(),
    }
    return jwt.encode(payload, private_key, algorithm=algorithm)
