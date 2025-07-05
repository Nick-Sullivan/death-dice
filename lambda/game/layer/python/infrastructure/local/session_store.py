from datetime import datetime, timezone

from domain_models import SessionItem
from domain_services.interfaces import SessionNotFoundException, ISessionStore, ITransaction


class SessionStore(ISessionStore) :
  """Creates, updates and destroys entries in the Connection table"""
  
  def __init__(self):
    self.cache = {}

  def create(self, item: SessionItem, transaction: ITransaction):
    item.version = 0
    item.modified_at = datetime.now(timezone.utc)
    self.cache[item.id] = item

  def get(self, id: str) -> SessionItem:
    if id not in self.cache:
      raise SessionNotFoundException(f'Unable to get connection {id}')
    return self.cache[id]
  
  def set(self, item: SessionItem, transaction: ITransaction):
    assert item.id is not None
    item.version += 1
    item.modified_at = datetime.now(timezone.utc)
    self.cache[item.id] = item

  def delete(self, item: SessionItem, transaction: ITransaction):
    self.cache.pop(item.id)
  
