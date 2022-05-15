import boto3
from botocore.exceptions import ClientError


def transaction_fail_logs(func):
  def inner(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except ClientError as e:
      print(e)
      print(e.response)
  return inner

def transaction_retry(func, max_attempts=5):
  """Decorator, reattempts processing if it gets a TransactionCanceledException"""

  def inner(*args, **kwargs):
    attempts = 0
    while attempts < max_attempts:
      attempts += 1
      try:
        return func(*args, **kwargs)
      except ClientError as e:
        if e.response['Error']['Code'] == 'TransactionCanceledException':
          print('EXCEPTION: TransactionCanceledException')
        else:
          raise e
          
        if attempts == max_attempts:
          raise e

  return inner


class DatabaseReader:
  """Created to perform multiple database reads in a single transaction.
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.transact_write_items
  
  Example usage:
  
    with DatabaseReader() as conn:
      response = conn.read(..., Object)  # returns object with default attributes
      response2 = conn.read(..., Object)
    print(response)                      # attributes are now populated
  """

  client = boto3.client('dynamodb', region_name='ap-southeast-2')

  def __init__(self):
    self.items = []

  def __enter__(self):
    assert self.items == [], 'Tried creating a new transaction before the previous one was completed'
    return self
  
  def __exit__(self, type, value, traceback):
    if not self.items:
      return
    
    self._transact()

  def _transact(self):
    items = self.items
    self.items = [] # clear in case of exception
    responses = self.client.transact_get_items(TransactItems=[i[0] for i in items])

    print(f'transact_get_items: {responses}')

    for response, (_, obj) in zip(responses['Responses'], items):
      if 'Item' not in response:
        continue
      new_obj = obj.from_query(response['Item'])
      obj.update_from(new_obj)

  def read(self, request, cls):
    obj = cls()
    self.items.append((request, obj))
    self._transact() # do it now, so thatgame state is read first. TODO
    return obj
  
  def query(self, kwargs):
    """Queries are executed immediately because they don't support transactions"""
    response = self.client.query(**kwargs)
    print(f'query response: {response}')
    return response


class DatabaseWriter:
  """Created to perform multiple database writes in a single transaction.
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.transact_write_items
  
  Example usage:
  
    with DatabaseWriter() as conn:
      conn.write(...) # not executed
      conn.write(...) # not executed
    # both are now executed
  """
  MAX_ITEMS = 25
  client = boto3.client('dynamodb', region_name='ap-southeast-2')
  
  def __init__(self):
    self.items = []

  def __enter__(self):
    assert self.items == [], 'Tried creating a new transaction before the previous one was completed'
    return self

  def __exit__(self, type, value, traceback):
    print(f'transact_write_items ({len(self.items)}): {self.items}')

    if not self.items:
      return

    items = self.items
    self.items = [] # clear in case of exception
    self.client.transact_write_items(TransactItems=items)

  def write(self, item):
    assert len(item) < self.MAX_ITEMS, 'Too many write transactions'
    self.items.append(item)
