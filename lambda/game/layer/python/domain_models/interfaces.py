
from abc import ABC, abstractmethod


class ITransaction(ABC):

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass

    @abstractmethod
    def write(self, item):
        pass

    @abstractmethod
    def then(self, func):
        pass

    @abstractmethod
    def clear(self):
        pass
