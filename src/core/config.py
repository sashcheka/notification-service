import os

from pydantic_settings import BaseSettings


class RabbitMQSettings(BaseSettings):
    USER: str = os.environ["RABBITMQ_USER"]
    PASSWORD: str = os.environ["RABBITMQ_PASSWORD"]
    HOST: str = os.environ["RABBITMQ_HOST"]
    PORT: str = os.environ["RABBITMQ_PORT"]

    @property
    def url(self) -> str:
        return f"amqp://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/"


class Settings(BaseSettings):
    rabbitmq: RabbitMQSettings = RabbitMQSettings()


settings = Settings()
