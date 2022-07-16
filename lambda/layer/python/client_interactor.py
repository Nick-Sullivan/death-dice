import boto3
import json
import os
from botocore.exceptions import ClientError

from model.game_items import GameState


class ClientNotifier:
  """Responsible for sending messages to players"""

  def __init__(self) -> None:
    url = os.environ['GATEWAY_URL'].replace('wss', 'https')
    self.gatewayapi = None
    if url:
      self.gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=url)

  @staticmethod
  def get_connection_id(player_id):
    """Mapping from the player ID (in the database) to the connection ID (websockets)"""
    return player_id

  def send_notification(self, player_ids, data):
    """Sends data to all the connections"""
    for player_id in player_ids:
      connection_id = self.get_connection_id(player_id)
      self._post_to_connection(connection_id, data)

  def _post_to_connection(self, connection_id, data):
    """Sends data to the API gateway"""
    if self.gatewayapi is None:
      return

    try:
      self.gatewayapi.post_to_connection(
          ConnectionId=connection_id,
          Data=json.dumps(data)
      )
    except ClientError as e:
      if e.response['Error']['Code'] == 'GoneException':
        return
      raise e

  def send_game_state_update(self, game: GameState):

    # Player and turn info
    player_output = []
    for player in game.players:
      entry = {
        'id': player.id,
        'nickname': 'Mr Eleven' if player.id == game.mr_eleven else player.nickname,
        'turnFinished': player.finished,
        'winCount': player.win_counter,
        'rollResult': player.outcome.value,
      }

      # Combine dice rolls into one
      if player.rolls:

        dice_roll = player.rolls[0]
        for dr in player.rolls[1:]:
          dice_roll += dr

        entry['rollTotal'] = sum(dice_roll.values)
        entry['diceValue'] = json.dumps(dice_roll.to_json())

      player_output.append(entry)

    # Order by player joined time TODO
    player_output.sort(key=lambda x: x['id'])
      
    # Send it
    message = {
      'action': 'gameState',
      'data': {
        'players': player_output,
        'round': {'complete': game.round_finished},
      },
    }
    print(f'game_state_update: {message}')
    self.send_notification([p.id for p in game.players], message)


def lambda_handler(func):
  """Decorator, parses all AWS lambda input"""
  
  def wrapper(event, context):

    connection_id = event['requestContext']['connectionId']

    request=json.loads(event['body']) if 'body' in event else {}

    func(connection_id, request)

    return {'statusCode': 200}

  return wrapper
