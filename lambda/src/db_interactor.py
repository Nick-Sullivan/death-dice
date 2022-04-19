import boto3
import datetime
import random
import string
from boto3.dynamodb.conditions import Key

class DatabaseInteractor:
  """Creates and destroys entries in the DyanmoDB table"""
  
  def __init__(self):
    dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
    self.connections = dynamodb.Table('DeathDiceConnections')
    self.games = dynamodb.Table('DeathDiceGames')

  # Players

  def get_player_id(self, connection_id):
    return connection_id
  
  def get_connection_id(self, player_id):
    return player_id
  
  def _create_player_id(self, connection_id):
    return connection_id

  def create_player(self, connection_id):
    player_id = self._create_player_id(connection_id)
    self.connections.put_item(
      Item={"Id": player_id}
    )
    return player_id
      
  def delete_player(self, player_id):
    return self.connections.delete_item(
      Key={"Id": player_id}
    )

  def set_nickname(self, player_id, nickname):
    return self.connections.update_item(
      Key={"Id": player_id},
      UpdateExpression='set Nickname = :s',
      ExpressionAttributeValues={':s': nickname},
    )

  def get_nickname(self, player_id):
    item = self._get_player(player_id)
    return item['Nickname']

  def get_game_id(self, player_id):
    item = self._get_player(player_id)
    return item['GameId']

  def _get_player(self, player_id):
    response = self.connections.get_item(
      Key={"Id": player_id}
    )
    return response.get('Item')

  # Games

  def create_game(self, player_id):
    """A game must have at least 1 player in it"""
    game_id = self._create_unique_game_id()

    self.games.put_item(
      Item={'Id': game_id}
    )

    self.join_game(player_id, game_id)

    return game_id

  def _create_unique_game_id(self):
    """Creates a unique lobby code that doesn't yet exist in the database"""
    gen = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    game_id = gen()

    while self.game_exists(game_id):
      game_id = gen()

    return game_id

  def delete_game(self, game_id):
    return self.games.delete_item(
      Key={"Id": game_id}
    )

  def get_player_ids_in_game(self, game_id):
    items = self._get_players_in_game(game_id)
    return [item['Id'] for item in items]

  def join_game(self, player_id, game_id):
    if not self.game_exists(game_id):
      raise ValueError(f'Game ID does not exist: {game_id}')

    return self.connections.update_item(
      Key={"Id": player_id},
      UpdateExpression='set GameId = :s',
      ExpressionAttributeValues={':s': game_id},
    )
  
  def game_exists(self, game_id):
    return self._get_game(game_id) != None

  def _get_game(self, game_id):
    response = self.games.get_item(
      Key={"Id": game_id}
    )
    return response.get('Item')

  def _get_players_in_game(self, game_id):
    response = self.connections.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key('GameId').eq(game_id),
    )
    return response['Items']

  # Rounds

  # def get_game_state(self, game_id):
    # connections = self._get_connections_in_game(game_id)
    # print(connections)

    # player_states = {
    #   c['Id']: {'nickname': c['Nickname']}
    #   for c in connections
    # }

    # state = {
    #   "players": {
    #     player_states
    #   }
    # }

    # return state

