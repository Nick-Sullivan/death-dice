import boto3
import json
import os
from botocore.exceptions import ClientError


class ClientNotifier:
  """Responsible for sending messages to players"""

  def __init__(self) -> None:
    url = os.environ['GATEWAY_URL'].replace('wss', 'https')
    self.gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=url)
    print('hi')

  @staticmethod
  def get_connection_id(player_id):
    return player_id

  def send_notification(self, player_ids, data):
    """Sends data to all the connections"""
    for player_id in player_ids:
      connection_id = self.get_connection_id(player_id)
      self._post_to_connection(connection_id, data)

  def _post_to_connection(self, connection_id, data):
    """Sends data to the API gateway"""
    try:
      self.gatewayapi.post_to_connection(
          ConnectionId=connection_id,
          Data=json.dumps(data)
      )
    except ClientError as e:
      if e.response['Error']['Code'] == 'GoneException':
        return
      raise e
