import os
from datetime import datetime, timezone

from dao.db_client import get_client
from dao.transaction_writer import default_transaction
from model import ConnectionItem


class ConnectionNotFoundException(Exception):
  pass


class ConnectionDao:
  """Creates, updates and destroys entries in the Connection table"""
  
  def __init__(self):
    self.client = get_client()
    self.table_name = os.environ['PROJECT']

  def create(self, item):
    assert isinstance(item, ConnectionItem)

    item.version = 0
    item.modified_at = datetime.now(timezone.utc)

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
    item.modified_at = datetime.now(timezone.utc)

    transaction.write({
      'Put': {
        'TableName': self.table_name,
        'Item': ConnectionItem.serialise(item),
        'ConditionExpression': f'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': str(item.version-1)}},
      }
    })

  @default_transaction
  def delete(self, item, transaction=None):
    assert isinstance(item, ConnectionItem)
    transaction.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'id': {'S': item.id}},
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': str(item.version)},
        },
      }
    })
  
  def is_valid_nickname(self, nickname):
    invalid_names = {'MR ELEVEN', 'MRELEVEN', 'MR 11', 'MR11'}
    return (
      2 <= len(nickname) <= 20
      and nickname.upper().strip() not in invalid_names
    )
  