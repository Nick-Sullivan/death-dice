import boto3

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
players = dynamodb.Table('DeathDicePlayers')
games = dynamodb.Table('DeathDiceGames')


class DatabaseInteractor:
  """Creates and destroys entries in the DyanmoDB table"""
  
  def __init__(self):
    self.players = players
    self.games = games

  # Players

  def create_player(self, player_id):
    self.players.put_item(
      Item={"Id": player_id}
    )
      
  def delete_player(self, player_id):
    self.players.delete_item(
      Key={"Id": player_id}
    )

  def update_player_attribute(self, player_id, attribute, value):
    self.players.update_item(
      Key={"Id": player_id},
      UpdateExpression=f'set {attribute} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_player_attribute(self, player_id, attribute):
    item = self._get_player(player_id)
    return item[attribute]

  def _get_player(self, player_id):
    item = self.players.get_item(
      Key={"Id": player_id}
    )
    return item.get('Item')

  # Games

  def create_game(self, game_id):
    self.games.put_item(
      Item={'Id': game_id}
    )

  def delete_game(self, game_id):
    return self.games.delete_item(
      Key={"Id": game_id}
    )

  def game_exists(self, game_id):
    return self._get_game(game_id) != None

  def _get_game(self, game_id):
    response = self.games.get_item(
      Key={"Id": game_id}
    )
    return response.get('Item')

  def get_player_ids_in_game(self, game_id):
    items = self._get_players_in_game(game_id)
    return [item['Id'] for item in items]

  def _get_players_in_game(self, game_id):
    response = self.players.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key('GameId').eq(game_id),
    )
    return response['Items']

  # Rounds

  # def get_game_state(self, game_id):
  #   players = self._get_players_in_game(game_id)

  #   player_states = [
  #     {
  #       'id': p['Id'],
  #       'nickname': p['Nickname'],
  #     }
  #     for p in players
  #   ]

  #   state = {
  #     "players": player_states
  #   }

  #   return state

