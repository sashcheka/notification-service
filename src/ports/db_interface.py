from abc import ABC, abstractmethod


class IDB(ABC):
    @abstractmethod
    def save_message(self, data):
        pass
