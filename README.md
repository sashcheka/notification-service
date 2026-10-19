# Notification Service

An event-driven notification service built with **Python** and **RabbitMQ**, developed as part of a Python Backend internship in 2024.

The service processes password reset events, validates JWT tokens, stores message data in MongoDB, and sends email notifications through AWS SES.

It is designed to work alongside the [User Management Service](https://github.com/sashcheka/user-management-service).

## Tech Stack

- **Language:** Python 3.10
- **Message Broker:** RabbitMQ, Pika
- **Database:** MongoDB, PyMongo
- **Email Service:** AWS SES, Boto3
- **Validation:** Pydantic, PyJWT
- **Infrastructure:** Docker, Docker Compose, LocalStack
- **Testing:** Pytest, unittest.mock
- **CI/CD:** GitHub Actions, pre-commit

## Features

- Asynchronous communication between services via RabbitMQ
- Event-driven processing of password reset requests
- JWT validation for password reset links
- Email notifications using AWS SES
- MongoDB storage for notification messages
- Configurable retry handling for failed messages
- Dead-letter queue (DLQ) for messages exceeding the retry limit
- Message acknowledgment and error handling
- Unit tests with mocked external dependencies

## Architecture

The service follows a ports-and-adapters approach to separate business logic from external integrations.

### Main Components

- `services/` — Message processing and business logic
- `adapters/` — RabbitMQ, MongoDB, AWS SES, and JWT implementations
- `ports/` — Interfaces for external dependencies
- `models/` — Pydantic message schemas
- `core/` — Configuration and email templates
- `tests/` — Unit tests

### Message Processing Flow

1. User Management Service publishes a password reset event to RabbitMQ.
2. Notification Service consumes the message.
3. The message is parsed and validated using Pydantic.
4. The password reset JWT is validated.
5. Message data is stored in MongoDB.
6. An email notification is sent through AWS SES.
7. The RabbitMQ message is acknowledged.

### Failure Handling

The service includes basic retry logic for failed message processing.

Failed messages are republished with an incremented retry counter. After the configured retry limit, messages are rejected and routed to a dead-letter queue.

This is an educational implementation; delivery guarantees and transactional consistency require further improvements for production use.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Running RabbitMQ and LocalStack services

### Run the Application

The project uses an external Docker network named `common_network`.

Start the User Management Service first to create the shared network and provide RabbitMQ and LocalStack.

Then run:

```bash
git clone https://github.com/sashcheka/notification-service.git
cd notification-service

docker compose up -d --build
```

The service runs as a background RabbitMQ consumer rather than exposing an HTTP API.

Environment configuration is provided through `.env`. Use local development credentials and avoid committing real secrets.

## Testing

The project uses Pytest and mocked adapters to test message processing and JWT validation.

Run the test environment:

```bash
docker compose -f docker-compose-test.yml up -d --build

docker compose -f docker-compose-test.yml run --rm web-test pytest tests/ --cov=src

docker compose -f docker-compose-test.yml down
```

GitHub Actions is configured to run automated checks and tests.

## Related Project

[User Management Service](https://github.com/sashcheka/user-management-service) — provides authentication, user management, and password reset events.

## Project Status

Educational internship project (2024).

The project demonstrates event-driven communication, message processing, external service integrations, and basic reliability mechanisms.

It is not intended for production use without further improvements to error handling, message delivery guarantees, and security.
