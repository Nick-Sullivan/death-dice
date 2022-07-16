import pytest
from botocore.exceptions import ClientError
from unittest.mock import MagicMock, patch

from dao import TransactionWriter, concurrency_retry, default_transaction

path = 'dao.transaction_writer'


class TestDatabaseWriter:

  @staticmethod
  def fake_transact_write_items(TransactItems):
    return {'Responses': TransactItems}

  @pytest.fixture
  def writer(self):
    dbw = TransactionWriter()
    dbw.client = MagicMock()
    dbw.client.transact_write_items = MagicMock(side_effect=self.fake_transact_write_items)
    return dbw

  def test_write(self, writer):
    with writer:
      writer.write('apple')
      assert not writer.client.transact_write_items.called
    assert writer.client.transact_write_items.called


@concurrency_retry
def fake_concurrency_function(a_list):
  a_list.append('call') # count iterations with mutable argument

  if len(a_list) < 3:
    raise ClientError(
      error_response={'Error': {'Code': 'TransactionCanceledException'}},
      operation_name='operation_name',
    )
  else:
    raise Exception('Some other exception')
  

def test_concurrency_retry():
  """Three concurrency exceptions, one other exception"""
  a_list = []
  with pytest.raises(Exception):
    fake_concurrency_function(a_list)
  assert len(a_list) == 3


@default_transaction
def fake_transaction_function(transaction=None):
  return transaction


def test_default_transaction():
  assert fake_transaction_function(3) == 3

  with patch(f'{path}.TransactionWriter') as mock:
    bleh = fake_transaction_function()
    assert bleh == mock().__enter__()
  
