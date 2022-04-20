import boto3
import json

domain_name = 'v2p7p69isj.execute-api.ap-southeast-2.amazonaws.com'
stage = 'production'
url = f'https://{domain_name}/{stage}'
gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=url)


class PlayerInteractor:
  """Responsible for sending messages to players"""

  def __init__(self):
    self.gatewayapi = gatewayapi

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





# class PlayerInteractor:
#   """Responsible for sending messages to players"""

#   def __init__(self, connection_id, endpoint_url, request):
#     """Initialise

#     :param str connection_id: connection of the player responsible for this interaction
#     :param str endpoint_url: URL of the gateway API
#     :param dict request: the payload sent from the player
#     """
#     self.connection_id = connection_id
#     self.player_id = connection_id
#     self.gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)
#     self.request = request

#   @classmethod
#   def from_lambda_event(cls, event):
#     """Create a PlayerInteractor object from an AWS Lambda event"""
#     request_context = event['requestContext']

#     return PlayerInteractor(
#       connection_id=request_context['connectionId'],
#       endpoint_url=f'https://{request_context["domainName"]}/{request_context["stage"]}',
#       request=json.loads(event['body']) if 'body' in event else {}
#     )
  
#   @staticmethod
#   def get_connection_id(player_id):
#     return player_id

#   def send_response(self, response):
#     """Sends a response to the websocket that sent the request, includes a copy of the request"""
#     full_response = {**self.request, **response}
#     self._post_to_connection(self.connection_id, full_response)

#   def send_notification(self, player_ids, data):
#     """Sends data to all the connections"""
#     for player_id in player_ids:
#       connection_id = self.get_connection_id(player_id)
#       self._post_to_connection(connection_id, data)

#   def _post_to_connection(self, connection_id, data):
#     """Sends data to the API gateway"""
#     self.gatewayapi.post_to_connection(
#         ConnectionId=connection_id,
#         Data=json.dumps(data)
#     )
