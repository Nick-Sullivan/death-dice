import boto3
from boto3.dynamodb.conditions import Key
from enum import Enum


class GameAttribute(Enum):
  ID = 'Id'
  MR_ELEVEN = 'MrEleven'


class GameDao:
  """Creates, updates and destroys entries in the Games table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDiceGames')

  def create_game(self, id):
    assert isinstance(id, str)
    self.table.put_item(
      Item={
        GameAttribute.ID.value: id,
      }
    )

  def delete_game(self, id):
    assert isinstance(id, str)
    return self.table.delete_item(
      Key={GameAttribute.ID.value: id}
    )

  def update_game_attribute(self, id, attribute, value):
    assert isinstance(attribute, GameAttribute)

    self.table.update_item(
      Key={GameAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_game_attribute(self, id, attribute):
    assert isinstance(attribute, GameAttribute)

    item = self._get_game(id)
    return item.get(attribute.value)

  def game_exists(self, id):
    return self._get_game(id) != None

  def _get_game(self, id):
    item = self.table.get_item(
      Key={GameAttribute.ID.value: id}
    )
    return item.get('Item')
