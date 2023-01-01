from unittest.mock import patch

from create_game import create_game
from model import ConnectionAction, ConnectionItem, GameAction

path = 'create_game'


@patch(f'{path}.TransactionWriter')
@patch(f'{path}.client_notifier')
@patch(f'{path}.game_dao')
@patch(f'{path}.connection_dao')
def test_create_game(connection_dao, game_dao, client_notifier, transaction_mock):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id', modified_action=ConnectionAction.CREATE_CONNECTION)
  game_dao.create_unique_game_id.return_value = 'ABCD'

  create_game({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  assert connection_dao.set.call_args.args[0].game_id == 'ABCD'
  assert connection_dao.set.call_args.args[0].modified_action == ConnectionAction.JOIN_GAME
  assert connection_dao.set.call_args.args[1] == transaction_mock().__enter__()
  assert game_dao.create.call_args.args[0].id == 'ABCD'
  assert game_dao.create.call_args.args[0].modified_action == GameAction.CREATE_GAME
  assert game_dao.create.call_args.args[0].modified_by == 'nicks_connection_id'
  assert game_dao.create.call_args.args[1] == transaction_mock().__enter__()
  assert client_notifier.send_notification.call_args.args[1]['data'] == 'ABCD'
  client_notifier.send_game_state_update.assert_called_once()
