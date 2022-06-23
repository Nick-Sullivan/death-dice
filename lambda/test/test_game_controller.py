import os
import pytest
import sys
from contextlib import ExitStack
from copy import deepcopy
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath('./lambda/src/python'))
from model.game_items import ConnectionItem, GameItem, PlayerItem, GameState, RollItem
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

  def test_get_state(self, obj):
    items_raw = [
      {
        'id': {'S': 'BFRJ'},
        'item_type': {'S': 'GAME'}
      },
      {
        'nickname': {'S': 'AVERAGE_JOE'},
        'item_type': {'S': 'PLAYER'}
      }
    ]
    obj.game_dao.get_items_with_game_id = MagicMock(side_effect=lambda *x: items_raw)

    result = obj.get_state('BFRJ')
    assert result.game.id == 'BFRJ'
    assert result.players[0].nickname == 'AVERAGE_JOE'
    assert not result.rolls

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
    # Update all items even if only one is changed, for optimistic concurrency
    new_state = deepcopy(state)
    new_state.players[0].version = 3
    obj.save_state(conn, state, new_state)
    obj.game_dao.set.assert_any_call(conn, state.game)
    obj.game_dao.set.assert_any_call(conn, new_state.players[0])
    obj.game_dao.set.assert_any_call(conn, state.rolls[0])
    assert not obj.game_dao.create.called
    assert not obj.game_dao.delete.called
  
  def test_disconnect_pre_game(self, obj):
    obj.connection_dao.get = MagicMock(return_value=ConnectionItem(game_id=None))
    obj.save_state = MagicMock()

    obj.disconnect('connection id')
    obj.connection_dao.delete.assert_called_once()
    obj.save_state.assert_not_called()

  def test_disconnect_last_player_in_game(self, obj):
    obj.connection_dao.get = MagicMock(return_value=ConnectionItem(game_id='GAME'))
    obj.get_state = MagicMock(return_value=GameState(game=GameItem(), players=[], rolls=[]))
    obj.save_state = MagicMock()

    obj.disconnect('connection id')
    obj.connection_dao.delete.assert_called_once()
    obj.save_state.assert_called_once()
    assert obj.save_state.call_args.args[2] == None

  def test_disconnect_two_players_in_game(self, obj):
    obj.connection_dao.get = MagicMock(return_value=ConnectionItem(game_id='GAME'))
    obj.get_state = MagicMock(return_value=GameState(
      game=GameItem(),
      players=[PlayerItem(finished=False), PlayerItem(finished=False)],
      rolls=[]
    ))
    obj.save_state = MagicMock()
    obj.send_game_state_update = MagicMock()

    obj.disconnect('connection id')
    obj.connection_dao.delete.assert_called_once()
    obj.save_state.assert_called_once()
    assert isinstance(obj.save_state.call_args.args[2], GameState)
