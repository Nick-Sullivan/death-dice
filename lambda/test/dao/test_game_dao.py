
import os
import pytest
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath('./lambda/src/python'))
from dao.game import DynamodbItem, GameDao
from model.dynamodb_item import DynamodbItem


class TestGameDao:

  @pytest.fixture
  def obj(self):
    return GameDao()

  @pytest.fixture
  def conn(self):
    return MagicMock()

  def test_init(self, obj):
    assert isinstance(obj, GameDao)

  def test_set(self, obj, conn):
    obj.set(conn, DynamodbItem(game_id="game_id", id="id", version=2))
    conn.write.assert_called_once_with({
      'Update': {
        'TableName': 'DeathDice',
        'Key': {'game_id': {'S': 'game_id'}, 'id': {'S': 'id'}},
        'ConditionExpression': 'attribute_exists(game_id) AND attribute_exists(id) AND version = :v',
        'UpdateExpression': 'SET version = :2',
        'ExpressionAttributeValues': {':2': {'N': '3'}, ':v': {'N': '2'}},
      }
    })
