
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
