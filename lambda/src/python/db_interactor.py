import boto3

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
players = dynamodb.Table('DeathDicePlayers')
games = dynamodb.Table('DeathDiceGames')
rolls = dynamodb.Table('DeathDiceRolls')


class DatabaseInteractor:
  """Creates and destroys entries in the DyanmoDB table"""
  
  def __init__(self):
    self.players = players
    self.games = games
    self.rolls = rolls

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
    return item.get(attribute)

  def _get_player(self, player_id):
    item = self.players.get_item(
      Key={"Id": player_id}
    )
    return item.get('Item')

  def get_player_ids_in_game(self, game_id):
    items = self._get_players_in_game(game_id)
    return [item['Id'] for item in items]

  def _get_players_in_game(self, game_id):
    response = self.players.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key('GameId').eq(game_id),
    )
    return response['Items']

  # Games

  def create_game(self, game_id):
    self.games.put_item(
      Item={
        'Id': game_id,
        'IsRoundComplete': True,
      }
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

  def update_game_attribute(self, game_id, attribute, value):
    self.games.update_item(
      Key={"Id": game_id},
      UpdateExpression=f'set {attribute} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_game_attribute(self, game_id, attribute):
    item = self._get_game(game_id)
    return item.get(attribute)

  def _get_game(self, game_id):
    item = self.games.get_item(
      Key={"Id": game_id}
    )
    return item.get('Item')

  # Rolls

  def create_roll(self, game_id, player_id, dice_value):
    self.rolls.put_item(
      Item={
        'Id': player_id, # TODO: generate a random ID
        'GameId': game_id,
        'PlayerId': player_id,
        'DiceValue': dice_value,
      }
    )

  def delete_rolls_in_game(self, game_id):
    round_ids = self.get_roll_ids_in_game(game_id)
    for round_id in round_ids:
      self.delete_roll(round_id)

  def delete_roll(self, roll_id):
    return self.rolls.delete_item(
      Key={"Id": roll_id}
    )

  def get_roll_ids_in_game(self, game_id):
    items = self._get_rolls_in_game(game_id)
    return [item['Id'] for item in items]

  def _get_rolls_in_game(self, game_id):
    response = self.rolls.query(
      IndexName='GameIndex',
      KeyConditionExpression=Key('GameId').eq(game_id),
    )
    return response['Items']

  def update_roll_attribute(self, roll_id, attribute, value):
    self.rolls.update_item(
      Key={"Id": roll_id},
      UpdateExpression=f'set {attribute} = :s',
      ExpressionAttributeValues={':s': value},
    )

  def get_roll_attribute(self, roll_id, attribute):
    item = self._get_roll(roll_id)
    return item[attribute]

  def _get_roll(self, roll_id):
    item = self.rolls.get_item(
      Key={"Id": roll_id}
    )
    return item.get('Item')
