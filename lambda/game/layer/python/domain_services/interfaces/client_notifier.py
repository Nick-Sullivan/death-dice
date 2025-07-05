
from abc import ABC, abstractmethod
from typing import Dict, List


class IClientNotifier(ABC):
  
  @abstractmethod
  def send_notification(self, connection_ids: List[str], data: Dict):
    pass
