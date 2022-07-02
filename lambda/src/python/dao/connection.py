import os
from datetime import datetime, timezone

from model.game_items import ConnectionItem


class ConnectionDao:
  """Creates, updates and destroys entries in the Connection table"""
  
  item_class = ConnectionItem

  def __init__(self):
    self.table_name = os.environ['PROJECT'] + 'Connections'

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

  def get(self, connection, id):
    assert isinstance(id, str)

    return connection.read({
      'Get': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
      }
    }, self.item_class)

  def set(self, connection, item):
    assert isinstance(item, self.item_class)
    assert item.id is not None

    item.version += 1

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
        'ExpressionAttributeValues': values,
      }
    })

  def delete(self, connection, id):
    assert isinstance(id, str)
    connection.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
        'ConditionExpression': f'attribute_exists(id)',
      }
    })
  