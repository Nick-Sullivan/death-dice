
import os
import pytest
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath('./lambda/src/python'))
from model.game_items import GameState, lookup_item_class, ItemType, GameItem, PlayerItem, RollItem


@pytest.mark.parametrize('item_type, expected', [
  pytest.param(ItemType.GAME, GameItem, id='game item'),
  pytest.param(ItemType.PLAYER, PlayerItem, id='player item'),
  pytest.param(ItemType.ROLL, RollItem, id='roll item'),
])
def test_lookup_item_class(item_type, expected):
  result = lookup_item_class(item_type)
  assert result == expected


class TestGameState:

  @pytest.fixture
  def obj(self):
    return GameState(
      game=GameItem(id='g'),
      players=[PlayerItem(id='p1'), PlayerItem(id='p2')],
      rolls=[RollItem(id='r')],
    )
  
  def test_flatten(self, obj):
    result = obj.flatten()
    expected_ids = ['p1', 'p2', 'r', 'g']
    assert [r.id for r in result] == expected_ids
