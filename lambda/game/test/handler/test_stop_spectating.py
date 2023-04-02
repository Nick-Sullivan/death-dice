import pytest
from unittest.mock import patch

from stop_spectating import stop_spectating
from model import ConnectionAction, ConnectionItem, GameAction, GameState, Player, Spectator

path = 'stop_spectating'


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


def test_not_a_spectator(game_dao, client_notifier):

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

  stop_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  game_dao.set.assert_not_called()
  client_notifier.send_game_state_update.assert_called_once()


def test_become_a_player(game_dao, client_notifier):

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

  stop_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  game_dao.set.assert_called_once()
  assert game_dao.set.call_args.args[0].spectators == []
  assert game_dao.set.call_args.args[0].players[0].id == 'nicks_connection_id'
  client_notifier.send_game_state_update.assert_called_once()
