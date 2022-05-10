
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

  def get_rolls_with_turn_id(self, connection, turn_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'turn_index',
      'KeyConditionExpression': f'turn_id = :id',
      'ExpressionAttributeValues': {':id': {'S': turn_id}},
    })
    return [self.item_class.from_query(i) for i in response['Items']]

  def get_rolls_with_game_id(self, connection, game_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'game_index',
      'KeyConditionExpression': f'game_id = :id',
      'ExpressionAttributeValues': {':id': {'S': game_id}},
    })
    return [self.item_class.from_query(i) for i in response['Items']]
