
from dataclasses import dataclass
from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class RollItem(DynamodbItem):
  turn_id: str = None
  game_id: str = None
  dice: str = None


class RollDao(BaseDao):
  """Creates, updates and destroys entries in the Rolls table"""

  table_name = 'DeathDiceRolls'
  item_class = RollItem
