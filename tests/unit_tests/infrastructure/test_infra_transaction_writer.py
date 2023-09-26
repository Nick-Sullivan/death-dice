import pytest
from unittest.mock import MagicMock

from infrastructure.cloud.transaction_writer import TransactionWriter

path = 'infrastructure.cloud.transaction_writer'


class TestDatabaseWriter:

  @staticmethod
  def fake_transact_write_items(TransactItems):
    return {'Responses': TransactItems}

  @pytest.fixture
  def writer(self):
    dbw = TransactionWriter(MagicMock())
    dbw.client.transact_write_items = MagicMock(side_effect=self.fake_transact_write_items)
    return dbw

  def test_write(self, writer):
    with writer.create() as transaction:
      transaction.write('apple')
      assert not writer.client.transact_write_items.called
    assert writer.client.transact_write_items.called
