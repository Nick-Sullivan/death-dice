
from base_dao import BaseDao, TableAttribute


class RollAttribute(TableAttribute):
  ID = ('Id', 'S')
  TURN_ID = ('TurnId', 'S')
  DICE = ('Dice', 'S')


class RollDao(BaseDao):
  """Creates, updates and destroys entries in the Rolls table"""

  table_name = 'DeathDiceRolls'
  attribute = RollAttribute

  def create(self, connection, id, turn_id, dice):
    assert isinstance(id, str)
    connection.write({
      'Put': {
        'TableName': self.table_name,
        'Item': {
          RollAttribute.ID.key: {RollAttribute.ID.type: id},
          RollAttribute.TURN_ID.key: {RollAttribute.TURN_ID.type: turn_id},
          RollAttribute.DICE.key: {RollAttribute.DICE.type: dice},
        },
        'ConditionExpression': f'attribute_not_exists({RollAttribute.ID.key})',
      }
    })

  def get_rolls_with_turn_id(self, connection, turn_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'TurnIndex',
      'KeyConditionExpression': f'{RollAttribute.TURN_ID.key} = :id',
      'ExpressionAttributeValues': {':id': {RollAttribute.TURN_ID.type: turn_id}},
    })
    return [self._parse_item(i) for i in response['Items']]
