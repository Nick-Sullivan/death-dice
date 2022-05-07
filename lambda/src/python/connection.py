import boto3


class DatabaseConnection:
  """Created to perform multiple database writes in a single transaction.
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.transact_write_items
  
  Example usage:
  
    with DatabaseConnection() as conn:
      conn.write(...) # executed at end of scope
      conn.read(...)  # executed immediately
      conn.write(...) # executed at end of scope
  """

  client = boto3.client('dynamodb', region_name='ap-southeast-2')
  
  def __init__(self):
    self.items = []

  def __enter__(self):
    """Clear all items from the previous transaction"""
    assert self.items == [], 'Tried creating a new transaction before the previous one was completed'
    return self

  def __exit__(self, type, value, traceback):
    """Execute all items in a single transaction"""
    if self.items:
      print(f'transact_write_items: {self.items}')
      self.client.transact_write_items(TransactItems=self.items)
      self.items = []

  def write(self, item):
    """Writing will be executed as part of a transaction when __exit__ is called"""
    self.items.append(item)

  def read(self, item):
    """Reading is executed immediately"""
    response = self.client.transact_get_items(TransactItems=[item])
    print(f'read response: {response}')
    return response['Responses'][0]

  def query(self, kwargs):
    """Queries are executed immediately"""
    response = self.client.query(**kwargs)
    print(f'query response: {response}')
    return response
