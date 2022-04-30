import boto3
import random
import string
from boto3.dynamodb.conditions import Key
from enum import Enum


class GameAttribute(Enum):
  ID = 'Id'
  MR_ELEVEN = 'MrEleven'


class GameDao:
  """Creates, updates and destroys entries in the Games table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDiceGames')

  def create(self, id):
    assert isinstance(id, str)
    self.table.put_item(
      Item={
        GameAttribute.ID.value: id,
      }
    )

  def delete(self, id):
    assert isinstance(id, str)
    return self.table.delete_item(
      Key={GameAttribute.ID.value: id}
    )

  def set_attribute(self, id, attribute, value):
    assert isinstance(attribute, GameAttribute)

    self.table.update_item(
      Key={GameAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_attribute(self, id, attribute):
    assert isinstance(attribute, GameAttribute)

    item = self._get(id)
    return item.get(attribute.value)

  def game_exists(self, id):
    return self._get(id) != None

  def _get(self, id):
    item = self.table.get_item(
      Key={GameAttribute.ID.value: id}
    )
    return item.get('Item')

  def create_unique_id(self):
    """Creates a unique game ID that doesn't yet exist in the database"""
    gen = lambda: ''.join(random.choices(string.ascii_uppercase, k=4))

    game_id = gen()
    while self.game_exists(game_id):
      game_id = gen()

    return game_id