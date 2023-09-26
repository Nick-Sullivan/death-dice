import random
import string
from datetime import datetime, timezone

from domain_models import GameState
from domain_services.interfaces import GameNotFoundException, IGameStore, ITransaction


class GameStore(IGameStore) :
  """Creates, updates and destroys entries in the Connection table"""
  
  def __init__(self):
    self.cache = {}

  def create(self, item: GameState, transaction: ITransaction):
    item.version = 0
    item.modified_at = datetime.now(timezone.utc)
    self.cache[item.id] = item

  def get(self, id: str) -> GameState:
    if id not in self.cache:
      raise GameNotFoundException(f'Invalid game {id}')
    return self.cache[id]

  def set(self, item: GameState, transaction: ITransaction):
    assert item.id is not None
    item.version += 1
    item.modified_at = datetime.now(timezone.utc)
    self.cache[item.id] = item

  def delete(self, item: GameState, transaction: ITransaction):
    self.cache.pop(item.id)
  
  def create_unique_game_id(self) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=4))
  
  def is_valid_game_id(self, game_id: str) -> bool:
    return True
