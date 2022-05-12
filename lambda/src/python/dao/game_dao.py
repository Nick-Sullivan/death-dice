from dataclasses import dataclass
import random
import string
from dao.base_dao import BaseDao, DynamodbItem


@dataclass
class GameItem(DynamodbItem):
  mr_eleven: str = None
  num_players: int = None
  round_finished: bool = None
  version: int = None


class GameDao(BaseDao):
  """Creates, updates and destroys entries in the Games table"""
  
  table_name = 'DeathDiceGames'
  item_class = GameItem

  def create_unique_id(self, connection):
    """Creates a unique game ID that doesn't yet exist in the database"""
    gen = lambda: ''.join(random.choices(string.ascii_uppercase, k=4))

    game_id = gen()
    # while self.exists(connection, game_id):
    #   game_id = gen()

    return game_id

  def set(self, connection, item):
    """Overwrites base function with an added version condition check"""
    assert isinstance(item, self.item_class)
    assert item.id is not None

    query = item.to_query()

    expressions = []
    values = {}
    for i, (key, value) in enumerate(query.items()):
      if key == 'id':
        continue
      expressions.append(f'{key} = :{i}')
      values[f':{i}'] = value

    update_expression = f'SET ' + ', '.join(expressions)

    values[':v'] = {'N': str(item.version-1)}

    connection.write({
      'Update': {
        'TableName': self.table_name,
        'Key': {'id': {'S': item.id}},
        'ConditionExpression': f'attribute_exists(id) AND version = :v',
        'UpdateExpression': update_expression,
        "ExpressionAttributeValues": values,
      }
    })
