import pytest
from unittest.mock import patch

from disconnect import disconnect
from model import ConnectionItem, GameState

path = 'disconnect'


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


def test_disconnect_no_game(connection_dao):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id')

  disconnect({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  connection_dao.delete.assert_called_once_with('nicks_connection_id')


def test_disconnect_only_player(connection_dao, game_dao, transaction_mock):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id', game_id='game_id')
  game_dao.get.return_value = GameState(id='game_id', mr_eleven='', round_finished=False, players=[0])

  disconnect({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  connection_dao.delete.assert_called_once_with('nicks_connection_id', transaction_mock().__enter__())
  game_dao.delete.assert_called_once_with('game_id', transaction_mock().__enter__())


@pytest.mark.skip
def test_disconnect_round_finished():
  pass


@pytest.mark.skip
def test_disconnect_many_players():
  pass