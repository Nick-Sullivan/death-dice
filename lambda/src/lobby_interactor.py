import boto3
import datetime
import random
import string


class LobbyInteractor:
  """Creates and destroys entries in the DyanmoDB table"""
  
  def __init__(self, table_name):
    dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")
    self.table = dynamodb.Table(table_name)

  def scan(self):
    """Returns a JSON of table contents"""
    return self.table.scan()

  def create(self, id):
    # ttl = (int)((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())

    return self.table.put_item(
      Item={
        "ConnectionId": id,
        # "TimeToLive": ttl,
        "Info": {
            "ColumnA": "bleh",
        },
      }
    )
      
  def delete(self, id):
    return self.table.delete_item(
      Key={"ConnectionId": id}
    )

  # def generate_lobby_id(self):
  #   """Creates a unique lobby code that doesn't yet exist in the database"""
  #   lobby_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

  #   while self.lobby_exists(lobby_id):
  #     lobby_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

  #   return lobby_id

  # def lobby_exists(self, lobby_id):
  #   """Returns true if the lobby ID already exists in the database"""
  #   return "Item" in self.get_lobby(lobby_id)

  # def get_lobby(self, lobby_id):
  #   return self.table.get_item(
  #     Key={"LobbyId": lobby_id}
  #   )
