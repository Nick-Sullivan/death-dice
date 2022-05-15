from dataclasses import dataclass
from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class TurnItem(DynamodbItem):
  game_id: str = None
  player_id: str = None
  finished: bool = None
  outcome: str = None


class TurnDao(BaseDao):
  """Creates, updates and destroys entries in the Turns table"""
  
  table_name = 'DeathDiceTurns'
  item_class = TurnItem
