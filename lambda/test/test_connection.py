

import os
import pytest
import sys
from unittest.mock import MagicMock
sys.path.append(os.path.abspath('./lambda/src/python'))
from connection import DatabaseReader, DatabaseWriter
from dao.player_dao import PlayerItem


class TestDatabaseReader:

  @staticmethod
  def fake_transact_get_items(TransactItems):
    return {'Responses': [{'Item': t} for t in TransactItems]}

  @pytest.fixture
  def reader(self):
    dbr = DatabaseReader()
    dbr.client = MagicMock()
    dbr.client.transact_get_items = MagicMock(side_effect=self.fake_transact_get_items)
    return dbr

  def test_read(self, reader):
    with reader:
      read1 = reader.read({'id': {'S': 'apple'}}, PlayerItem)
      read2 = reader.read({'id': {'S': 'banana'}}, PlayerItem)
      assert isinstance(read1, PlayerItem)
      assert isinstance(read2, PlayerItem)
      assert read1.id == None
      assert read2.id == None
    assert read1.id == 'apple'
    assert read2.id == 'banana'


class TestDatabaseWriter:

  @staticmethod
  def fake_transact_write_items(TransactItems):
    return {'Responses': TransactItems}

  @pytest.fixture
  def writer(self):
    dbw = DatabaseWriter()
    dbw.client = MagicMock()
    dbw.client.transact_write_items = MagicMock(side_effect=self.fake_transact_write_items)
    return dbw

  def test_write(self, writer):
    with writer:
      writer.write('apple')
      assert not writer.client.transact_write_items.called
    assert writer.client.transact_write_items.called