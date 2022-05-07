from base_dao import BaseDao, TableAttribute


class TurnAttribute(TableAttribute):
  ID = ('Id', 'S')
  GAME_ID = ('GameId', 'S')
  PLAYER_ID = ('PlayerId', 'S')
  FINISHED = ('Finished', 'BOOL')
  OUTCOME = ('Outcome', 'S')


class TurnDao(BaseDao):
  """Creates, updates and destroys entries in the Turns table"""
  
  table_name = 'DeathDiceTurns'
  attribute = TurnAttribute

  def create(self, connection, id, game_id, player_id):
    assert isinstance(id, str)
    connection.write({
      'Put': {
        'TableName': self.table_name,
        'Item': {
          TurnAttribute.ID.key: {TurnAttribute.ID.type: id},
          TurnAttribute.GAME_ID.key: {TurnAttribute.GAME_ID.type: game_id},
          TurnAttribute.PLAYER_ID.key: {TurnAttribute.PLAYER_ID.type: player_id},
          TurnAttribute.FINISHED.key: {TurnAttribute.FINISHED.type: False},
        },
        'ConditionExpression': f'attribute_not_exists({TurnAttribute.ID.key})',
      }
    })

  def get_turns_with_player_id(self, connection, player_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'PlayerIndex',
      'KeyConditionExpression': f'{TurnAttribute.PLAYER_ID.key} = :id',
      'ExpressionAttributeValues': {':id': {TurnAttribute.PLAYER_ID.type: player_id}},
    })
    return [self._parse_item(i) for i in response['Items']]

  def get_turns_with_game_id(self, connection, game_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'GameIndex',
      'KeyConditionExpression': f'{TurnAttribute.GAME_ID.key} = :id',
      'ExpressionAttributeValues': {':id': {TurnAttribute.GAME_ID.type: game_id}},
    })
    return [self._parse_item(i) for i in response['Items']]
