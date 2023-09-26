
from typing import Dict, List
from domain_services.interfaces import IClientNotifier


class ClientNotifier(IClientNotifier):

    def __init__(self):
        self.notifications = {}
  
    def send_notification(self, connection_ids: List[str], data: Dict):
        for connection_id in connection_ids:
            if connection_id not in self.notifications:
                self.notifications[connection_id] = []
            self.notifications[connection_id].append(data)

    def clear(self, connection_id: str):
        self.notifications.pop(connection_id, None)
