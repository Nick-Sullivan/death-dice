from datetime import datetime, timezone
from domain_models import WebsocketConnectionItem
from domain_services.interfaces import ITransaction, IWebsocketConnectionStore, WebsocketConnectionNotFoundException

        
class WebsocketConnectionStore(IWebsocketConnectionStore) :
  
  def __init__(self, client, table_name):
    self.client = client
    self.table_name = table_name

  def create(self, item: WebsocketConnectionItem, transaction: ITransaction):
    assert isinstance(item, WebsocketConnectionItem)

    item.version = 0
    item.modified_at = datetime.now(timezone.utc)

    transaction.write({
      'Put': {
        'TableName': self.table_name,
        'Item': WebsocketConnectionItem.serialise(item),
        'ConditionExpression': 'attribute_not_exists(id)',
      }
    })

  def get(self, id: str) -> WebsocketConnectionItem:
    assert isinstance(id, str)

    item = self.client.get_item(**{
      'TableName': self.table_name,
      'Key': {'connection_id': {'S': id}},
    })

    if 'Item' not in item:
      raise WebsocketConnectionNotFoundException(f'Unable to get websocket connection {id}')

    return WebsocketConnectionItem.deserialise(item['Item'])

  def set(self, item: WebsocketConnectionItem, transaction: ITransaction):
    assert isinstance(item, WebsocketConnectionItem)
    assert item.connection_id is not None
    
    item.version += 1
    item.modified_at = datetime.now(timezone.utc)

    transaction.write({
      'Put': {
        'TableName': self.table_name,
        'Item': WebsocketConnectionItem.serialise(item),
        'ConditionExpression': 'attribute_exists(connection_id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': str(item.version-1)}},
      }
    })

  def delete(self, item: WebsocketConnectionItem, transaction: ITransaction):
    assert isinstance(item, WebsocketConnectionItem)
    transaction.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'connection_id': {'S': item.connection_id}},
        'ConditionExpression': 'attribute_exists(connection_id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': str(item.version)},
        },
      }
    })
  