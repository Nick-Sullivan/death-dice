
from abc import ABC, abstractmethod

from domain_models import SessionItem

from .transaction_writer import ITransaction


class SessionNotFoundException(Exception):
  pass


class ISessionStore(ABC):
  
  @abstractmethod
  def create(self, item: SessionItem):
    pass

  @abstractmethod
  def get(self, id: str) -> SessionItem:
    pass

  @abstractmethod
  def set(self, item: SessionItem, transaction: ITransaction):
    pass

  @abstractmethod
  def delete(self, item: SessionItem, transaction: ITransaction):
    pass
