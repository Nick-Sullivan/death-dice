import boto3
from boto3.dynamodb.conditions import Key
from enum import Enum


class PlayerAttribute(Enum):
  ID = 'Id'
  NICKNAME = 'Nickname'
  GAME_ID = 'GameId'
  WIN_COUNTER = 'WinCounter'


class PlayerDao:
  """Creates, updates and destroys entries in the Players table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDicePlayers')

  def create(self, id):
    assert isinstance(id, str)
    self.table.put_item(
      Item={PlayerAttribute.ID.value: id}
    )
      
  def delete(self, id):
    assert isinstance(id, str)
    self.table.delete_item(
      Key={PlayerAttribute.ID.value: id}
    )

  def set_attribute(self, id, attribute, value):
    assert isinstance(attribute, PlayerAttribute)

    self.table.update_item(
      Key={PlayerAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_attribute(self, id, attribute):
    assert isinstance(attribute, PlayerAttribute)

    item = self.get(id)
    return item.get(attribute.value)

  def get(self, id):
    item = self.table.get_item(
      Key={PlayerAttribute.ID.value: id}
    )
    return self._parse_item(item['Item'])

  def get_players_with_game_id(self, game_id):
    response = self.table.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key(PlayerAttribute.GAME_ID.value).eq(game_id),
    )
    return [self._parse_item(i) for i in response['Items']]

  def _parse_item(self, item):
    if PlayerAttribute.WIN_COUNTER.value in item:
      item[PlayerAttribute.WIN_COUNTER.value] = int(item[PlayerAttribute.WIN_COUNTER.value])
    return item