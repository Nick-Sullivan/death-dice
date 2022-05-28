import os
import pytest
import sys
from contextlib import ExitStack
from copy import deepcopy
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath('./lambda/src/python'))
from model.game import GameItem, PlayerItem, GameState, RollItem
from game_controller import GameController


class TestGameController:

  @pytest.fixture(scope='function')
  def obj(self):
    with ExitStack() as stack:
      stack.enter_context(patch.object(GameController, 'client_notifier'))
      stack.enter_context(patch.object(GameController, 'connection_dao'))
      stack.enter_context(patch.object(GameController, 'game_dao'))
      yield GameController()

  @pytest.fixture(scope='class')
  def conn(self):
    return 'conn'

  @pytest.fixture(scope='class')
  def state(self):
    return GameState(
      game=GameItem(game_id='ABCD', id='ABCD', mr_eleven='hi'),
      players=[PlayerItem(game_id='ABCD', id='P1')],
      rolls=[RollItem(game_id='ABCD', id='R1')]
    )

  def test_save_state_create(self, obj, conn, state):
    obj.save_state(conn, None, state)
    obj.game_dao.create.assert_any_call(conn, state.game)
    obj.game_dao.create.assert_any_call(conn, state.players[0])
    obj.game_dao.create.assert_any_call(conn, state.rolls[0])
    assert not obj.game_dao.delete.called
    assert not obj.game_dao.set.called

  def test_save_state_delete(self, obj, conn, state):
    obj.save_state(conn, state, None)
    obj.game_dao.delete.assert_any_call(conn, state.game)
    obj.game_dao.delete.assert_any_call(conn, state.players[0])
    obj.game_dao.delete.assert_any_call(conn, state.rolls[0])
    assert not obj.game_dao.create.called
    assert not obj.game_dao.set.called

  def test_save_state_set(self, obj, conn, state):
    new_state = deepcopy(state)
    new_state.players[0].version = 3

    obj.save_state(conn, state, new_state)
    obj.game_dao.set.assert_any_call(conn, new_state.players[0])

    assert obj.game_dao.set.call_count == 1
    assert not obj.game_dao.create.called
    assert not obj.game_dao.delete.called