import os
import boto3
from datetime import datetime, timezone
from dao.db_wrapper import TransactionWriter
from model.game_items import ConnectionItem


class ConnectionNotFoundException(Exception):
  pass


def default_transaction(func):
  """Decorator, provides a transaction if not provided"""
  def wrapper(*args, **kwargs):
    fill_kwargs_with_args(func, args, kwargs)

    if kwargs.get('transaction') is not None:
      return func(**kwargs)

    with TransactionWriter() as kwargs['transaction']:
      return func(**kwargs)

  return wrapper


def fill_kwargs_with_args(func, args, kwargs):
  kwargs.update(zip(func.__code__.co_varnames, args))


class ConnectionDao:
  """Creates, updates and destroys entries in the Connection table"""
  
  client = boto3.client('dynamodb', region_name='ap-southeast-2')

  def __init__(self):
    self.table_name = os.environ['PROJECT']

  def create(self, item):
    assert isinstance(item, ConnectionItem)

    item.version = 0
    item.created_on=datetime.now(timezone.utc)

    self.client.put_item(**{
      'TableName': self.table_name,
      'Item': ConnectionItem.serialise(item),
      'ConditionExpression': 'attribute_not_exists(id)',
    })

  def get(self, id) -> ConnectionItem:
    assert isinstance(id, str)

    item = self.client.get_item(**{
      'TableName': self.table_name,
      'Key': {'id': {'S': id}},
    })

    if 'Item' not in item:
      raise ConnectionNotFoundException(f'Unable to get connection {id}')

    return ConnectionItem.deserialise(item['Item'])

  @default_transaction
  def set(self, item, transaction=None):
    assert isinstance(item, ConnectionItem)
    assert item.id is not None

    item.version += 1

    query = ConnectionItem.serialise(item)

    expressions = []
    values = {}
    for i, (key, value) in enumerate(query.items()):
      if key == 'id':
        continue
      expressions.append(f'{key} = :{i}')
      values[f':{i}'] = value

    update_expression = f'SET ' + ', '.join(expressions)

    values[':v'] = {'N': str(item.version-1)}

    transaction.write({
      'Update': {
        'TableName': self.table_name,
        'Key': {'id': {'S': item.id}},
        'ConditionExpression': f'attribute_exists(id) AND version = :v',
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': values,
      }
    })

  @default_transaction
  def delete(self, id, transaction=None):
    assert isinstance(id, str)
    transaction.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
        'ConditionExpression': f'attribute_exists(id)',
      }
    })
  
  def is_valid_nickname(self, nickname):
    invalid_names = {'MR ELEVEN', 'MRELEVEN', 'MR 11', 'MR11'}
    return (
      2 <= len(nickname) <= 20
      and nickname.upper not in invalid_names
    )