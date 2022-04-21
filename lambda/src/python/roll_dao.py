import boto3
from boto3.dynamodb.conditions import Key
from enum import Enum


class RollAttribute(Enum):
  ID = 'Id'
  GAME_ID = 'GameId'
  PLAYER_ID = 'PlayerId'
  DICE_VALUES = 'DiceValues'
  ROLL_RESULT = 'RollResult'


class RollDao:
  """Creates, updates and destroys entries in the Rolls table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDiceRolls')

  def create_roll(self, game_id, player_id, dice_values):
    self.table.put_item(
      Item={
        RollAttribute.ID.value: player_id, # TODO: generate a random ID
        RollAttribute.GAME_ID.value: game_id,
        RollAttribute.PLAYER_ID.value: player_id,
        RollAttribute.DICE_VALUES.value: dice_values,
      }
    )

  def delete_roll(self, id):
    return self.table.delete_item(
      Key={RollAttribute.ID.value: id}
    )

  def update_roll_attribute(self, id, attribute, value):
    assert isinstance(attribute, RollAttribute)

    self.table.update_item(
      Key={RollAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_roll_attribute(self, id, attribute):
    assert isinstance(attribute, RollAttribute)

    item = self._get_roll(id)

    value = item.get(attribute.value)

    if attribute == RollAttribute.DICE_VALUES and value is not None:
      return [int(v) for v in value]
      
    return value

  def _get_roll(self, id):
    item = self.table.get_item(
      Key={RollAttribute.ID.value: id}
    )
    return item.get('Item')

  def delete_rolls_in_game(self, game_id):
    round_ids = self.get_roll_ids_in_game(game_id)
    for round_id in round_ids:
      self.delete_roll(round_id)

  def get_roll_ids_in_game(self, game_id):
    items = self._get_rolls_in_game(game_id)
    return [item[RollAttribute.ID.value] for item in items]

  def _get_rolls_in_game(self, game_id):
    response = self.table.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key(RollAttribute.GAME_ID.value).eq(game_id),
    )
    return response['Items']
