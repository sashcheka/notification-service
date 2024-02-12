from abc import ABC, abstractmethod


class IMessageConsumerPort(ABC):

    @abstractmethod
    def consume_messages(self, queue: str, callback):
        pass
