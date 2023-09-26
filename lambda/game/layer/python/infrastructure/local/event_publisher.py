
from typing import Dict

from domain_services.interfaces import IEventPublisher


class EventPublisher(IEventPublisher):

  def __init__(self):
    self.events = {}

  def publish_event(self, source: str, detail_type: str, detail: Dict):
    if source not in self.events:
        self.events[source] = []
    self.events[source].append(detail)
