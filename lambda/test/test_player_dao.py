


import os
import pytest
import sys
sys.path.append(os.path.abspath('./lambda/src/python'))
from dao.player_dao import DynamodbItem, PlayerAttribute, PlayerDao, PlayerItem


class TestPlayerItem:

  @pytest.fixture
  def obj(self):
    return PlayerItem(id='hi', win_counter=2)

  def test_init(self, obj):
    assert isinstance(obj, DynamodbItem)

  def test_to_query(self, obj):
    result = obj.to_query()
    assert result == {'id': {'S': 'hi'}, 'win_counter': {'N': '2'}}
  
  def test_from_query(self):
    result = PlayerItem.from_query({'id': {'S': 'hi'}, 'win_counter': {'N': '2'}})
    assert result.id == 'hi'
    assert result.win_counter == 2

class TestPlayerDao:

  def test_init(self):
    a = PlayerDao()