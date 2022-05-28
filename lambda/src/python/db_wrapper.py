"""Wrappers for writing/reading to a DynamoDB in transactions"""
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
  It will also perform queries IMMEDIATELY AFTER the get's, but DynamoDB does not support queries in a single transaction.
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.transact_get_items
  
  Example usage:
  
    with DatabaseReader() as conn:
      response = conn.read(..., Object)  # returns object with default attributes
      response2 = conn.read(..., Object)
    print(response)                      # attributes are now populated
  """
  MAX_ITEMS = 25
  client = boto3.client('dynamodb', region_name='ap-southeast-2')

  def __init__(self):
    self.items = []
    self.queries = []

  def __enter__(self):
    assert self.items == [] and self.queries == [], f'Tried creating a new transaction before the previous one was completed, {self.items}, {self.queries}'
    return self
  
  def __exit__(self, type, value, traceback):
    if self.items:
      self._transact_read()
    if self.queries:
      self._transact_query()

  def _transact_read(self):
    items = self.items
    self.items = [] # clear in case of exception
    responses = self.client.transact_get_items(TransactItems=[i[0] for i in items])

    print(f'transact_get_items: {responses}')

    for response, (_, obj) in zip(responses['Responses'], items):
      if 'Item' not in response:
        continue
      new_obj = obj.from_query(response['Item'])
      obj.update_from(new_obj)

  def _transact_query(self):
    queries = self.queries
    self.queries = [] # clear in case of exception
    for kwargs, response_obj in queries:
      response = self.client.query(**kwargs)
      print(f'query_response: {response}')
      response_obj.items = [response_obj.item_cls.from_query(i) for i in response['Items']]

  def read(self, request, cls):
    assert len(request) < self.MAX_ITEMS, 'Too many reads for a transaction'
    obj = cls()
    self.items.append((request, obj))
    return obj
    
  def query(self, request, cls=None):
    return self.client.query(**request)['Items']
    # obj = QueryResponse(item_cls=cls)
    # self.queries.append((request, obj))
    # return obj


class QueryResponse:
  """Iterable query response, has no data until the DatabaseReader __exit__"""
  def __init__(self, item_cls):
    self.items = []
    self.item_cls = item_cls

  def __iter__(self):
    for item in self.items:
      yield item

  def __len__(self):
    return len(self.items)


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
    assert len(item) < self.MAX_ITEMS, 'Too many writes for a transaction'
    self.items.append(item)
