import random
import string
from base_dao import BaseDao, TableAttribute


class GameAttribute(TableAttribute):
  ID = ('Id', 'S')
  MR_ELEVEN = ('MrEleven', 'S')


class GameDao(BaseDao):
  """Creates, updates and destroys entries in the Games table"""
  
  table_name = 'DeathDiceGames'
  attribute = GameAttribute

  def create(self, connection, id):
    assert isinstance(id, str)
    connection.write({
      'Put': {
        'TableName': self.table_name,
        'Item': {GameAttribute.ID.key: {GameAttribute.ID.type: id}},
        'ConditionExpression': f'attribute_not_exists({GameAttribute.ID.key})',
      }
    })

  def create_unique_id(self, connection):
    """Creates a unique game ID that doesn't yet exist in the database"""
    gen = lambda: ''.join(random.choices(string.ascii_uppercase, k=4))

    game_id = gen()
    while self.exists(connection, game_id):
      game_id = gen()

    return game_id
