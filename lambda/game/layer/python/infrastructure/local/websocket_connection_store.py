from datetime import datetime, timezone

from domain_models import WebsocketConnectionItem
from domain_services.interfaces import ITransaction, IWebsocketConnectionStore, WebsocketConnectionNotFoundException


class WebsocketConnectionStore(IWebsocketConnectionStore) :
  
    def __init__(self):
        self.cache = {}

    def create(self, item: WebsocketConnectionItem, transaction: ITransaction):
        item.version = 0
        item.modified_at = datetime.now(timezone.utc)
        self.cache[item.connection_id] = item

    def get(self, id: str) -> WebsocketConnectionItem:
        if id not in self.cache:
            raise WebsocketConnectionNotFoundException(f'Unable to get websocket connection {id}')
        return self.cache[id]

    def set(self, item: WebsocketConnectionItem, transaction: ITransaction):
        item.version += 1
        item.modified_at = datetime.now(timezone.utc)
        self.cache[item.connection_id] = item

    def delete(self, item: WebsocketConnectionItem, transaction: ITransaction):
        self.cache.pop(item.connection_id)
  