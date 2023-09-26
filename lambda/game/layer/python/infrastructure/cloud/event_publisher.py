import json
from datetime import datetime, timedelta, timezone
from typing import Dict

from domain_services.interfaces import IEventPublisher


class EventPublisher(IEventPublisher):

    def __init__(self, client, project):
        self.client = client
        self.project = project

    def publish_event(self, source: str, detail_type: str, detail: Dict):
        self.client.put_events(
            Entries=[{
                'Source': f'{self.project}.{source}',
                'DetailType': detail_type,
                'Detail': json.dumps(detail),
                'Resources': [],
            }]
        )
