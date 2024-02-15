from abc import ABC, abstractmethod


class IMessageQueue(ABC):
    @abstractmethod
    def initialize_queue(self, queue_name: str):
        pass

    @abstractmethod
    def consume_messages(self, queue_name: str, callback):
        pass
