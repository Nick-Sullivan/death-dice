import json
import pytest
from unittest.mock import patch

from dao import GameNotFoundException
from join_game import join_game
from model import ConnectionAction, ConnectionItem, GameAction, GameState

path = 'join_game'


@pytest.fixture(autouse=True)
def client_notifier():
  with patch(f'{path}.client_notifier') as mock:
    yield mock


@pytest.fixture(autouse=True)
def connection_dao():
  with patch(f'{path}.connection_dao') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def game_dao():
  with patch(f'{path}.game_dao') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def transaction_mock():
  with patch(f'{path}.TransactionWriter') as mock:
    yield mock


def test_join_game_invalid_code(game_dao, client_notifier):
  game_dao.get.side_effect = GameNotFoundException

  join_game({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
    'body': json.dumps({'data': 'ABCD'})
  }, None)

  assert client_notifier.send_notification.call_args.args[0] == ['nicks_connection_id']
  assert client_notifier.send_notification.call_args.args[1] == {
    'action': 'joinGame',
    'error': 'Unable to join game: ABCD',
  }


def test_join_game(connection_dao, game_dao, client_notifier, transaction_mock):
  connection_dao.get.return_value = ConnectionItem('nicks_connection_id', modified_action=ConnectionAction.CREATE_CONNECTION)
  game_dao.get.return_value = GameState(
    id='ABCD',
    mr_eleven='',
    round_finished=True,
    players=[],
    modified_action=GameAction.CREATE_GAME,
    modified_by='nick',
  )

  join_game({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
    'body': json.dumps({'data': 'ABCD'})
  }, None)

  assert connection_dao.set.call_args.args[0].game_id == 'ABCD'
  assert connection_dao.set.call_args.args[0].modified_action == ConnectionAction.JOIN_GAME
  assert connection_dao.set.call_args.args[1] == transaction_mock().__enter__()
  assert game_dao.set.call_args.args[0].players[0].id == 'nicks_connection_id'
  assert game_dao.set.call_args.args[1] == transaction_mock().__enter__()
  assert game_dao.set.call_args.args[0].modified_action == GameAction.JOIN_GAME
  assert game_dao.set.call_args.args[0].modified_by == 'nicks_connection_id'
  assert client_notifier.send_notification.call_args.args[0] == ['nicks_connection_id']
  assert client_notifier.send_notification.call_args.args[1] == {
    'action': 'joinGame',
    'data': 'ABCD',
  }
