import boto3
from boto3.dynamodb.conditions import Key
from enum import Enum


class RollAttribute(Enum):
  ID = 'Id'
  TURN_ID = 'TurnId'
  DICE = 'Dice'


class RollDao:
  """Creates, updates and destroys entries in the Rolls table"""
  
  dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
  table = dynamodb.Table('DeathDiceRolls')

  def create(self, id, turn_id, dice):
    self.table.put_item(
      Item={
        RollAttribute.ID.value: id,
        RollAttribute.TURN_ID.value: turn_id,
        RollAttribute.DICE.value: dice,
      }
    )

  def delete(self, id):
    return self.table.delete_item(
      Key={RollAttribute.ID.value: id}
    )

  def set_attribute(self, id, attribute, value):
    assert isinstance(attribute, RollAttribute)

    self.table.update_item(
      Key={RollAttribute.ID.value: id},
      UpdateExpression=f'set {attribute.value} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_attribute(self, id, attribute):
    assert isinstance(attribute, RollAttribute)
    item = self._get(id)
    return item.get(attribute.value)      

  def _get(self, id):
    item = self.table.get_item(
      Key={RollAttribute.ID.value: id}
    )
    return item.get('Item')

  def get_rolls_with_turn_id(self, turn_id):
    response = self.table.query(
      IndexName='TurnIndex',
      KeyConditionExpression=Key(RollAttribute.TURN_ID.value).eq(turn_id),
    )
    return response['Items']
