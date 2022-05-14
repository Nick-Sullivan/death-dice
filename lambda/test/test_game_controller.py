import os
import pytest
import sys
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath('./lambda/src/python'))
from dao.game_dao import GameItem
from dao.player_dao import PlayerItem
from dao.roll_dao import RollItem
from dao.turn_dao import TurnItem
from game_controller import GameController


class TestGameController:

  @pytest.fixture(scope='class')
  def obj(self):
    with ExitStack() as stack:
      stack.enter_context(patch.object(GameController, 'client_notifier'))
      stack.enter_context(patch.object(GameController, 'player_dao'))
      stack.enter_context(patch.object(GameController, 'game_dao'))
      stack.enter_context(patch.object(GameController, 'roll_dao'))
      stack.enter_context(patch.object(GameController, 'turn_dao'))
      stack.enter_context(patch.object(GameController, 'db_writer'))
      stack.enter_context(patch.object(GameController, 'db_reader'))
      yield GameController()

  @pytest.fixture(scope='class')
  def conn(self):
    return 'conn'

  @pytest.fixture(scope='class')
  def game(self):
    return GameItem(id=2, mr_eleven='hi')

  def test__save_state_game_create(self, obj, conn, game):
    obj._save_state_game(conn, None, game)
    obj.game_dao.create.assert_called_with(conn, game)

  def test__save_state_game_delete(self, obj, conn, game):
    obj._save_state_game(conn, game, None)
    obj.game_dao.delete.assert_called_with(conn, game.id)

  def test__save_state_game_set(self, obj, conn, game):
    obj._save_state_game(conn, GameItem(id=game.id), game)
    obj.game_dao.set.assert_called_with(conn, game)
  
  @pytest.fixture(scope='class')
  def player(self):
    return PlayerItem(id=2, win_counter=1)

  def test__save_state_players_create(self, obj, conn, player):
    obj._save_state_players(conn, [], [player])
    assert not obj.player_dao.create.called
    obj.player_dao.set.assert_called_with(conn, player)

  def test__save_state_players_delete(self, obj, conn, player):
    obj._save_state_players(conn, [player], [])
    obj.player_dao.delete.assert_called_with(conn, player.id)

  def test__save_state_players_set(self, obj, conn, player):
    obj._save_state_players(conn, [PlayerItem(id=player.id)], [player])
    obj.player_dao.set.assert_called_with(conn, player)
  
  @pytest.fixture(scope='class')
  def turn(self):
    return TurnItem(id=2, finished=True)

  def test__save_state_turns_create(self, obj, conn, turn):
    obj._save_state_turns(conn, [], [turn])
    obj.turn_dao.create.assert_called_with(conn, turn)

  def test__save_state_turns_delete(self, obj, conn, turn):
    obj._save_state_turns(conn, [turn], [])
    obj.turn_dao.delete.assert_called_with(conn, turn.id)

  def test__save_state_turns_set(self, obj, conn, turn):
    obj._save_state_turns(conn, [TurnItem(id=turn.id)], [turn])
    obj.turn_dao.set.assert_called_with(conn, turn)
  
  @pytest.fixture(scope='class')
  def roll(self):
    return RollItem(id=2, dice='d')

  def test__save_state_rolls_create(self, obj, conn, roll):
    obj._save_state_rolls(conn, [], [roll])
    obj.roll_dao.create.assert_called_with(conn, roll)

  def test__save_state_rolls_delete(self, obj, conn, roll):
    obj._save_state_rolls(conn, [roll], [])
    obj.roll_dao.delete.assert_called_with(conn, roll.id)

  def test__save_state_rolls_set(self, obj, conn, roll):
    obj._save_state_rolls(conn, [RollItem(id=roll.id)], [roll])
    obj.roll_dao.set.assert_called_with(conn, roll)
