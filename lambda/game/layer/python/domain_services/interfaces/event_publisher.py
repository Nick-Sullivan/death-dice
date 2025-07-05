
from abc import ABC, abstractmethod
from typing import Dict


class IEventPublisher(ABC):
  
  @abstractmethod
  def publish_event(self, source: str, detail_type: str, detail: Dict):
    pass
