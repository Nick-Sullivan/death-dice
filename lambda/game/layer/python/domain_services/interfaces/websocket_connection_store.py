
from abc import ABC, abstractmethod
from domain_models import WebsocketConnectionItem
from .transaction_writer import ITransaction


class WebsocketConnectionNotFoundException(Exception):
  pass


class IWebsocketConnectionStore(ABC):
  
  @abstractmethod
  def create(self, item: WebsocketConnectionItem):
    pass

  @abstractmethod
  def get(self, id: str) -> WebsocketConnectionItem:
    pass

  @abstractmethod
  def set(self, item: WebsocketConnectionItem, transaction: ITransaction):
    pass

  @abstractmethod
  def delete(self, item: WebsocketConnectionItem, transaction: ITransaction):
    pass
 
