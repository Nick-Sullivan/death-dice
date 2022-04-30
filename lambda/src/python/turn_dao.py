import boto3
from boto3.dynamodb.conditions import Key
from enum import Enum


class TurnAttribute(Enum):
  ID = 'Id'
  GAME_ID = 'GameId'
  PLAYER_ID = 'PlayerId'
  FINISHED = 'Finished'
  OUTCOME = 'Outcome'


class TurnDao:
  """Creates, updates and destroys entries in the Turns table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDiceTurns')

  def create(self, id, game_id, player_id):
    assert isinstance(id, str)
    self.table.put_item(
      Item={
        TurnAttribute.ID.value: id,
        TurnAttribute.GAME_ID.value: game_id,
        TurnAttribute.PLAYER_ID.value: player_id,
        TurnAttribute.FINISHED.value: False,
      }
    )

  def delete(self, id):
    assert isinstance(id, str)
    return self.table.delete_item(
      Key={TurnAttribute.ID.value: id}
    )

  def set_attribute(self, id, attribute, value):
    assert isinstance(attribute, TurnAttribute)

    self.table.update_item(
      Key={TurnAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_attribute(self, id, attribute):
    assert isinstance(attribute, TurnAttribute)

    item = self._get(id)
    return item.get(attribute.value)

  def exists(self, id):
    return self._get(id) != None

  def _get(self, id):
    item = self.table.get_item(
      Key={TurnAttribute.ID.value: id}
    )
    return item.get('Item')

  def get_turns_with_player_id(self, player_id):
    response = self.table.query(
      IndexName='PlayerIndex',
      KeyConditionExpression=Key(TurnAttribute.PLAYER_ID.value).eq(player_id),
    )
    return response['Items']

  def get_turns_with_game_id(self, game_id):
    response = self.table.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key(TurnAttribute.GAME_ID.value).eq(game_id),
    )
    return response['Items']