import os
from datetime import datetime, timezone

from model.dynamodb_item import DynamodbItem


class GameDao:
  """Creates, updates and destroys entries in the Game table"""

  item_class = DynamodbItem

  def __init__(self):
    self.table_name = os.environ['PROJECT']

  def create(self, connection, item):
    assert isinstance(item, self.item_class)

    item.version = 0
    item.created_on=datetime.now(timezone.utc)

    connection.write({
      'Put': {
        'TableName': self.table_name,
        'Item': item.to_query(),
        'ConditionExpression': f'attribute_not_exists(id)',
      }
    })

  def delete(self, connection, item):
    assert isinstance(item, self.item_class)

    connection.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'game_id': {'S': item.game_id}, 'id': {'S': item.id}},
        'ConditionExpression': f'attribute_exists(game_id) AND attribute_exists(id)',
      }
    })
  
  def set(self, connection, item):
    assert isinstance(item, self.item_class)
    assert item.id is not None

    item.version += 1

    query = item.to_query()

    expressions = []
    values = {}
    for i, (key, value) in enumerate(query.items()):
      if key in {'game_id', 'id'}:
        continue
      expressions.append(f'{key} = :{i}')
      values[f':{i}'] = value

    update_expression = f'SET ' + ', '.join(expressions)

    values[':v'] = {'N': str(item.version-1)}

    connection.write({
      'Update': {
        'TableName': self.table_name,
        'Key': {'game_id': {'S': item.game_id}, 'id': {'S': item.id}},
        'ConditionExpression': f'attribute_exists(game_id) AND attribute_exists(id) AND version = :v',
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': values,
      }
    })

  def get_items_with_game_id(self, connection, game_id):
    assert isinstance(game_id, str)
    return connection.query({
      'TableName': self.table_name,
      'KeyConditionExpression': f'game_id = :id',
      'ExpressionAttributeValues': {':id': {'S': game_id}},
    }, self.item_class)
