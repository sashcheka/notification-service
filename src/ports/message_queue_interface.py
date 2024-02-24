from abc import ABC, abstractmethod
from typing import Callable


class IMessageQueue(ABC):
    @abstractmethod
    def ensure_channel(self):
        pass

    @abstractmethod
    def initialize_queues(self, queue_name: str, exchange_name: str, routing_key: str):
        pass

    @abstractmethod
    def setup_dlq(self, dlq_name: str, dlx_name: str):
        pass

    @abstractmethod
    def consume_messages(self, queue_name: str, callback: Callable):
        pass
