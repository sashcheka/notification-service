import os

from pydantic_settings import BaseSettings


class MongoDBSettings(BaseSettings):
    USER: str = os.environ["MONGO_INITDB_ROOT_USERNAME"]
    PASSWORD: str = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
    HOST: str = os.environ["MONGO_INITDB_ROOT_HOST"]
    PORT: str = os.environ["MONGO_INITDB_ROOT_PORT"]

    @property
    def url(self) -> str:
        return f"mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/"


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
    mongodb: MongoDBSettings = MongoDBSettings()


settings = Settings()
