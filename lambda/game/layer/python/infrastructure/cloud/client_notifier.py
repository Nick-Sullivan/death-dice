import json
from typing import Dict, List

from botocore.exceptions import ClientError
from domain_services.interfaces import IClientNotifier


class ClientNotifier(IClientNotifier):
    """Responsible for sending messages to players"""

    def __init__(self, websocket) -> None:
        self.websocket = websocket

    def send_notification(self, connection_ids: List[str], data: Dict):
        """Sends data to all the connections"""
        print('sending notifications to ' + ','.join(connection_ids))
        for connection_id in connection_ids:
            self._post_to_connection(connection_id, data)

    def _post_to_connection(self, connection_id: str, data: Dict):
        """Sends data to the API gateway"""
        if self.websocket is None:
            return

        try:
            self.websocket.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(data)
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'GoneException':
                return
