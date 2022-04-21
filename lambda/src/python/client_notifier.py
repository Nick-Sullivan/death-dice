import boto3
import json


class ClientNotifier:
  """Responsible for sending messages to players"""

  url = f'https://hx45les9f5.execute-api.ap-southeast-2.amazonaws.com/production'
  gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=url)

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
    self.gatewayapi.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(data)
    )
