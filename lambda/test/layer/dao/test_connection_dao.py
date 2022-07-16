
# import os
# import pytest
# import sys
# from unittest.mock import MagicMock

# sys.path.append(os.path.abspath('./lambda/src/python'))
# from model.game_items import ConnectionItem
# from dao.connection import ConnectionDao


# class TestConnectionDao:

#   @pytest.fixture
#   def obj(self):
#     return ConnectionDao()

#   @pytest.fixture
#   def conn(self):
#     return MagicMock()

#   def test_init(self, obj):
#     assert isinstance(obj, ConnectionDao)

#   def test_set(self, obj, conn):
#     obj.set(conn, ConnectionItem(game_id="game_id", id="id", version=2))
#     conn.write.assert_called_once_with({
#       'Update': {
#         'TableName': 'DeathDiceConnections',
#         'Key': {'id': {'S': 'id'}},
#         'ConditionExpression': 'attribute_exists(id) AND version = :v',
#         'UpdateExpression': 'SET game_id = :0, version = :2',
#         'ExpressionAttributeValues': {':0': {'S': 'game_id'}, ':2': {'N': '3'}, ':v': {'N': '2'}},
#       }
#     })

