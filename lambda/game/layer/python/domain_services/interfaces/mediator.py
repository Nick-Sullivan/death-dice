
from abc import ABC, abstractmethod


class IMediator(ABC):
  
  @abstractmethod
  def send(self, command):
    pass
