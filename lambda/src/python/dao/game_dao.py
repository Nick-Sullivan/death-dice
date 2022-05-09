from dataclasses import dataclass
import random
import string
from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class GameItem(DynamodbItem):
  mr_eleven: str
  num_players: int
  round_finished: bool


class GameDao(BaseDao):
  """Creates, updates and destroys entries in the Games table"""
  
  table_name = 'DeathDiceGames'
  item_class = GameItem

  def create_unique_id(self, connection):
    """Creates a unique game ID that doesn't yet exist in the database"""
    gen = lambda: ''.join(random.choices(string.ascii_uppercase, k=4))

    game_id = gen()
    while self.exists(connection, game_id):
      game_id = gen()

    return game_id
