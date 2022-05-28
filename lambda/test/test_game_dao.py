
import os
import pytest
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath('./lambda/src/python'))
from dao.game import DynamodbItem, GameDao


class TestDynamodbItem:

  @pytest.fixture
  def obj(self):
    return DynamodbItem(id='hi', version=2)

  def test_init(self, obj):
    assert isinstance(obj, DynamodbItem)

  def test_to_query(self, obj):
    result = obj.to_query()
    assert result == {'id': {'S': 'hi'}, 'version': {'N': '2'}}
  
  def test_from_query(self):
    result = DynamodbItem.from_query({'id': {'S': 'hi'}, 'version': {'N': '2'}})
    assert result.id == 'hi'
    assert result.version == 2


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