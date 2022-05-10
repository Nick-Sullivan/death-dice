from dataclasses import dataclass
from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class PlayerItem(DynamodbItem):
  win_counter: int = None
  nickname: str = None
  game_id: str = None


class PlayerDao(BaseDao):
  """Creates, updates and destroys entries in the Players table"""
  
  table_name = 'DeathDicePlayers'
  item_class = PlayerItem

  def get_players_with_game_id(self, connection, game_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'game_index',
      'KeyConditionExpression': f'game_id = :id',
      'ExpressionAttributeValues': {':id': {'S': game_id}},
    })
    return [self.item_class.from_query(i) for i in response['Items']]
