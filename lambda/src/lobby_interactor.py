import boto3
import datetime
import random
import string
from boto3.dynamodb.conditions import Key

class LobbyInteractor:
  """Creates and destroys entries in the DyanmoDB table"""
  
  def __init__(self, table_name):
    dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
    self.table = dynamodb.Table(table_name)

  def create(self, connection_id):
    # ttl = (int)((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())

    return self.table.put_item(
      Item={
        "ConnectionId": connection_id,
        "LobbyId": "default",
      }
    )
      
  def delete(self, connection_id):
    return self.table.delete_item(
      Key={"ConnectionId": connection_id}
    )

  def join_lobby(self, connection_id, lobby_id):
    return self.table.update_item(
      Key={"ConnectionId": connection_id},
      UpdateExpression='set LobbyId = :s',
      ExpressionAttributeValues={':s': lobby_id},
    )
  
  def get_lobby_id(self, connection_id):
    item = self._get_item(connection_id)
    return item['LobbyId']

  def get_connection_ids_in_lobby(self, lobby_id):
    items = self._get_items_in_lobby(lobby_id)
    return [item['ConnectionId'] for item in items]

  def _get_item(self, connection_id):
    response = self.table.get_item(
      Key={"ConnectionId": connection_id}
    )
    return response['Item']

  def _get_items_in_lobby(self, lobby_id):
    response = self.table.query(
      IndexName='LobbyIndex',
      KeyConditionExpression=Key('LobbyId').eq(lobby_id),
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

