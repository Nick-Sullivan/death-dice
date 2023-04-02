import pytest
from unittest.mock import patch

from start_spectating import start_spectating
from model import ConnectionAction, ConnectionItem, GameAction, GameState, Player, Spectator

path = 'start_spectating'


@pytest.fixture(autouse=True)
def client_notifier():
  with patch(f'{path}.client_notifier') as mock:
    yield mock


@pytest.fixture(autouse=True)
def connection_dao():
  connection = ConnectionItem(id='nicks_connection_id', modified_action=ConnectionAction.CREATE_CONNECTION)
  with patch(f'{path}.connection_dao') as mock:
    mock.get.return_value = connection
    yield mock 


@pytest.fixture(autouse=True)
def game_dao():
  with patch(f'{path}.game_dao') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def calculate_turn_results():
  with patch(f'{path}.calculate_turn_results') as mock:
    mock.side_effect = lambda x: x
    yield mock


def test_already_a_spectator(game_dao, client_notifier):

  game_dao.get.return_value = GameState(
    id='game_id',
    mr_eleven='',
    round_id=0,
    round_finished=False,
    players=[],
    spectators=[Spectator(id='nicks_connection_id', account_id=None, nickname='nick')],
    modified_action=GameAction.START_SPECTATING,
    modified_by='nick',
  )

  start_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  game_dao.set.assert_not_called()
  client_notifier.send_game_state_update.assert_called_once()


def test_become_a_spectator(game_dao, client_notifier):
  game_dao.get.return_value = GameState(
    id='game_id',
    mr_eleven='',
    round_id=0,
    round_finished=False,
    players=[Player(id='nicks_connection_id', account_id=None, nickname='nick', win_counter=0, finished=False, outcome=None, rolls=[])],
    spectators=[],
    modified_action=GameAction.START_SPECTATING,
    modified_by='nick',
  )

  start_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  game_dao.set.assert_called_once()
  assert game_dao.set.call_args.args[0].players == []
  assert game_dao.set.call_args.args[0].spectators[0].id == 'nicks_connection_id'
  client_notifier.send_game_state_update.assert_called_once()


def test_become_a_spectator_round_finished(game_dao, client_notifier, calculate_turn_results):

  game_dao.get.return_value = GameState(
    id='game_id',
    mr_eleven='',
    round_id=0,
    round_finished=False,
    players=[
      Player(id='nicks_connection_id', account_id=None, nickname='nick', win_counter=0, finished=False, outcome=None, rolls=[]),
      Player(id='other', account_id=None, nickname='other', win_counter=0, finished=True, outcome=None, rolls=[]),
    ],
    spectators=[],
    modified_action=GameAction.START_SPECTATING,
    modified_by='nick',
  )

  start_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  calculate_turn_results.assert_called_once()
  game_dao.set.assert_called_once()
  assert game_dao.set.call_args.args[0].players[0].id == 'other'
  assert game_dao.set.call_args.args[0].spectators[0].id == 'nicks_connection_id'
  client_notifier.send_game_state_update.assert_called_once()
