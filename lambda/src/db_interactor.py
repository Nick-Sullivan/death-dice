import boto3
import datetime
import random
import string
from boto3.dynamodb.conditions import Key

class DatabaseInteractor:
  """Creates and destroys entries in the DyanmoDB table"""
  
  def __init__(self):
    dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
    self.connections = dynamodb.Table('UncomfortableQuestionsConnections')
    self.games = dynamodb.Table('UncomfortableQuestionsGames')

  # Connections

  def create_connection(self, connection_id):
    return self.connections.put_item(
      Item={
        "Id": connection_id,
      }
    )
      
  def delete_connection(self, connection_id):
    return self.connections.delete_item(
      Key={"Id": connection_id}
    )

  def _get_connection(self, connection_id):
    response = self.connections.get_item(
      Key={"Id": connection_id}
    )
    return response.get('Item')

  # Games

  def create_game(self, connection_id):
    game_id = 'new game'

    self.games.put_item(
      Item={
        'Id': game_id,
      }
    )

    self.join_game(connection_id, game_id)

  def delete_game(self, game_id):
    return self.games.delete_item(
      Key={"Id": game_id}
    )

  def get_game_id(self, connection_id):
    item = self._get_connection(connection_id)
    return item['GameId']

  def get_connection_ids_in_game(self, game_id):
    items = self._get_connections_in_game(game_id)
    return [item['Id'] for item in items]

  def join_game(self, connection_id, game_id):
    if not self.game_exists(game_id):
      raise ValueError(f'Game ID does not exist: {game_id}')

    return self.connections.update_item(
      Key={"Id": connection_id},
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

  def _get_connections_in_game(self, lobby_id):
    response = self.connections.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key('GameId').eq(lobby_id),
    )
    return response['Items']


  # def scan(self):
  #   """Returns a JSON of table contents"""
  #   return self.table.scan()
  # def generate_lobby_id(self):
  #   """Creates a unique lobby code that doesn't yet exist in the database"""
  #   lobby_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

  #   while self.lobby_exists(lobby_id):
  #     lobby_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

  #   return lobby_id

  # def lobby_exists(self, lobby_id):
  #   """Returns true if the lobby ID already exists in the database"""
  #   return "Item" in self.get_lobby(lobby_id)

