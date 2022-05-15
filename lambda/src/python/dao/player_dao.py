from dataclasses import dataclass

from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class PlayerItem(DynamodbItem):
  game_id: str = None
  nickname: str = None
  win_counter: int = None


class PlayerDao(BaseDao):
  """Creates, updates and destroys entries in the Players table"""
  
  table_name = 'DeathDicePlayers'
  item_class = PlayerItem
