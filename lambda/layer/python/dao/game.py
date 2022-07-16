import boto3
import os
import random
import string
from datetime import datetime, timezone
from dao.connection import default_transaction
from model.game_items import GameState


class GameNotFoundException(Exception):
  pass


class GameDao:
  """Creates, updates and destroys entries in the Game table"""

  client = boto3.client('dynamodb', region_name='ap-southeast-2')

  def __init__(self):
    self.table_name = os.environ['PROJECT']

  @default_transaction
  def create(self, item, transaction=None):
    assert isinstance(item, GameState)

    item.version = 0
    item.created_on=datetime.now(timezone.utc)

    transaction.write({
      'Put': {
        'TableName': self.table_name,
        'Item': GameState.serialise(item),
        'ConditionExpression': f'attribute_not_exists(id)',
      }
    })

  def get(self, id) -> GameState:

    if not self.is_valid_game_id(id):
      raise GameNotFoundException(f'Invalid game {id}')
    
    item = self.client.get_item(**{
      'TableName': self.table_name,
      'Key': {'id': {'S': id}}
    })

    if 'Item' not in item:
      raise GameNotFoundException(f'Unable to get game {id}')

    return GameState.deserialise(item['Item'])

  @default_transaction
  def set(self, item, transaction=None):
    assert isinstance(item, GameState)
    assert item.id is not None

    item.version += 1
    transaction.write({
      'Put': {
        'TableName': self.table_name,
        'Item': GameState.serialise(item),
        'ConditionExpression': f'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': str(item.version-1)}},
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
  
  def get_items_with_game_id(self, connection, game_id):
    assert isinstance(game_id, str)
    return connection.query({
      'TableName': self.table_name,
      'KeyConditionExpression': f'game_id = :id',
      'ExpressionAttributeValues': {':id': {'S': game_id}},
    }, self.item_class)

  def create_unique_game_id(self) -> str:
    items = self.client.scan(**{
      'TableName': self.table_name,
      'ProjectionExpression': 'id',
    })
    existing_ids = {item['id']['S'] for item in items['Items']}

    game_id = None
    while game_id in existing_ids or game_id is None:
      game_id = ''.join(random.choices(string.ascii_uppercase, k=4))
    
    return game_id

  def is_valid_game_id(self, game_id) -> bool:
    return isinstance(game_id, str) and len(game_id) == 4
