from base_dao import BaseDao, TableAttribute


class PlayerAttribute(TableAttribute):
  ID = ('Id', 'S')
  NICKNAME = ('Nickname', 'S')
  GAME_ID = ('GameId', 'S')
  WIN_COUNTER = ('WinCounter', 'N')


class PlayerDao(BaseDao):
  """Creates, updates and destroys entries in the Players table"""
  
  table_name = 'DeathDicePlayers'
  attribute = PlayerAttribute

  def create(self, connection, id):
    assert isinstance(id, str)
    connection.write({
      'Put': {
        'TableName': self.table_name,
        'Item': {PlayerAttribute.ID.key: {PlayerAttribute.ID.type: id}},
        'ConditionExpression': f'attribute_not_exists({PlayerAttribute.ID.key})',
      }
    })

  def get_players_with_game_id(self, connection, game_id):
    response = connection.query({
      'TableName': self.table_name,
      'IndexName': 'GameIndex',
      'KeyConditionExpression': f'{PlayerAttribute.GAME_ID.key} = :id',
      'ExpressionAttributeValues': {':id': {PlayerAttribute.GAME_ID.type: game_id}},
    })
    return [self._parse_item(i) for i in response['Items']]

  def _parse_item(self, item):
    # Example input
    # {
    #   'Nickname': {'S': 'Nick'},
    #   'Id': {'S': 'Rvf2mcfhSwMCE-Q='},
    #   'WinCounter': {'N': '0'},
    #   'GameId': {'S': 'NLDQ'}
    # }
    # Example output
    # {
    #   'Nickname': 'Nick',
    #   'Id': 'Rvf2mcfhSwMCE-Q=',
    #   'WinCounter': 0,
    #   'GameId': 'NLDQ',
    # }
    new_item = super()._parse_item(item)
      
    if PlayerAttribute.WIN_COUNTER.key in new_item:
      new_item[PlayerAttribute.WIN_COUNTER.key] = int(new_item[PlayerAttribute.WIN_COUNTER.key])

    return new_item
