import boto3
from boto3.dynamodb.conditions import Key
from enum import Enum


class PlayerAttribute(Enum):
  ID = 'Id'
  NICKNAME = 'Nickname'
  GAME_ID = 'GameId'


class PlayerDao:
  """Creates, updates and destroys entries in the Players table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDicePlayers')

  def create_player(self, id):
    assert isinstance(id, str)
    self.table.put_item(
      Item={PlayerAttribute.ID.value: id}
    )
      
  def delete_player(self, id):
    assert isinstance(id, str)
    self.table.delete_item(
      Key={PlayerAttribute.ID.value: id}
    )

  def update_player_attribute(self, id, attribute, value):
    assert isinstance(attribute, PlayerAttribute)

    self.table.update_item(
      Key={PlayerAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_player_attribute(self, id, attribute):
    assert isinstance(attribute, PlayerAttribute)

    item = self._get_player(id)
    return item.get(attribute.value)

  def _get_player(self, id):
    item = self.table.get_item(
      Key={PlayerAttribute.ID.value: id}
    )
    return item.get('Item')

  def get_player_ids_in_game(self, game_id):
    items = self._get_players_in_game(game_id)
    return [item[PlayerAttribute.ID.value] for item in items]

  def _get_players_in_game(self, game_id):
    response = self.table.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key(PlayerAttribute.GAME_ID.value).eq(game_id),
    )
    return response['Items']
