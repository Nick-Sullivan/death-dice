# import os
# import pytest
# import sys
# from unittest.mock import MagicMock
# from typing import List

# sys.path.append(os.path.abspath('./lambda/src/python'))
# from dao.db_wrapper import DatabaseReader, TransactionWriter
# from dao.connection import ConnectionItem


# class TestDatabaseReader:

#   @staticmethod
#   def fake_transact_get_items(TransactItems):
#     return {'Responses': [{'Item': t} for t in TransactItems]}

#   @staticmethod
#   def fake_query(kwarg):
#     return {'Items': [kwarg]}

#   @pytest.fixture
#   def reader(self):
#     dbr = DatabaseReader()
#     dbr.client = MagicMock()
#     dbr.client.transact_get_items = MagicMock(side_effect=self.fake_transact_get_items)
#     dbr.client.query = MagicMock(side_effect=self.fake_query)
#     return dbr

#   def test_read(self, reader):
#     with reader:
#       read1 = reader.read({'id': {'S': 'apple'}}, ConnectionItem)
#       read2 = reader.read({'id': {'S': 'banana'}}, ConnectionItem)
#       assert isinstance(read1, ConnectionItem)
#       assert isinstance(read2, ConnectionItem)
#       assert read1.id == None
#       assert read2.id == None
#     assert read1.id == 'apple'
#     assert read2.id == 'banana'

#   # def test_query(self, reader):
#   #   with reader:
#   #     result = reader.query({'kwarg': {'id': {'S': 'apple'}}}, ConnectionItem)
#   #     assert list(result) == []
#   #   # Iterable
#   #   for r in result:
#   #     assert isinstance(r, ConnectionItem)
#   #     assert r.id == 'apple'
#   #   # Convertable to list
#   #   result_list = list(result)
#   #   assert len(result_list) == 1
#   #   assert isinstance(result_list[0], ConnectionItem)
#   #   assert result_list[0].id == 'apple'


# class TestDatabaseWriter:

#   @staticmethod
#   def fake_transact_write_items(TransactItems):
#     return {'Responses': TransactItems}

#   @pytest.fixture
#   def writer(self):
#     dbw = TransactionWriter()
#     dbw.client = MagicMock()
#     dbw.client.transact_write_items = MagicMock(side_effect=self.fake_transact_write_items)
#     return dbw

#   def test_write(self, writer):
#     with writer:
#       writer.write('apple')
#       assert not writer.client.transact_write_items.called
#     assert writer.client.transact_write_items.called