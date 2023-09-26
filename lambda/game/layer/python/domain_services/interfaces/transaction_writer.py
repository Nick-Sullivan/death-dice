
from abc import ABC, abstractmethod

from domain_models.interfaces import ITransaction


class ITransactionWriter(ABC):

    @abstractmethod
    def create(self) -> ITransaction:
        pass
