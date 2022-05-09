from dataclasses import dataclass
from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class TurnItem(DynamodbItem):
  game_id: str
  player_id: str
  finished: bool
  outcome: str


class TurnDao(BaseDao):
  """Creates, updates and destroys entries in the Turns table"""
  
  table_name = 'DeathDiceTurns'
  item_class = TurnItem

  def get_turns_with_player_id(self, connection, player_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'player_index',
      'KeyConditionExpression': f'player_id = :id',
      'ExpressionAttributeValues': {':id': {'S': player_id}},
    })
    return [self.item_class.from_query(i) for i in response['Items']]

  def get_turns_with_game_id(self, connection, game_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'game_index',
      'KeyConditionExpression': f'game_id = :id',
      'ExpressionAttributeValues': {':id': {'S': game_id}},
    })
    return [self.item_class.from_query(i) for i in response['Items']]
