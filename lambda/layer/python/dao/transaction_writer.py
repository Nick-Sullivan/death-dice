"""Wrappers for writing to DynamoDB in transactions"""
from botocore.exceptions import ClientError

from dao.db_client import get_client


class TransactionWriter:
  """Created to perform multiple database writes in a single transaction.
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.transact_write_items
  
  Example usage:
  
    with TransactionWriter() as transaction:
      transaction.write(...) # not executed
      transaction.write(...) # not executed
    # both are now executed
  """
  MAX_ITEMS = 25
  
  def __init__(self):
    self.client = get_client()
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


def concurrency_retry(func, max_attempts=5):
  """Decorator, reattempts processing if a transaction fails because the data was changed"""

  def inner(*args, **kwargs):
    attempts = 0
    while attempts < max_attempts:
      attempts += 1

      try:

        return func(*args, **kwargs)

      except ClientError as e:
        
        if e.response['Error']['Code'] == 'TransactionCanceledException':
          print('Transaction aborted')
        else:
          raise e
          
        if attempts == max_attempts:
          raise e

  return inner


def default_transaction(func):
  """Decorator, provides a transaction if not provided"""
  def wrapper(*args, **kwargs):
    fill_kwargs_with_args(func, args, kwargs)

    if kwargs.get('transaction') is not None:
      return func(**kwargs)

    with TransactionWriter() as kwargs['transaction']:
      return func(**kwargs)

  return wrapper


def fill_kwargs_with_args(func, args, kwargs):
  kwargs.update(zip(func.__code__.co_varnames, args))
