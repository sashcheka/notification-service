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


class MongoDBSettings(BaseSettings):
    USER: str = os.environ["MONGO_INITDB_ROOT_USERNAME"]
    PASSWORD: str = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
    HOST: str = os.environ["MONGO_INITDB_ROOT_HOST"]
    PORT: str = os.environ["MONGO_INITDB_ROOT_PORT"]

    @property
    def url(self) -> str:
        return f"mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/"


class AWSSESSettings(BaseSettings):
    HOST: str = os.environ["LOCALSTACK_HOST"]
    PORT: str = os.environ["LOCALSTACK_PORT"]
    AWS_ACCESS_KEY_ID: str = os.environ["LOCALSTACK_AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY: str = os.environ["LOCALSTACK_AWS_SECRET_ACCESS_KEY"]
    REGION_NAME: str = os.environ["LOCALSTACK_REGION_NAME"]

    @property
    def endpoint_url(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"


class Settings(BaseSettings):
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    mongodb: MongoDBSettings = MongoDBSettings()
    awsses: AWSSESSettings = AWSSESSettings()


settings = Settings()
