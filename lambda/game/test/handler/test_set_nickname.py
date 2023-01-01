import json
import pytest
from unittest.mock import patch

from model import ConnectionAction, ConnectionItem
from set_nickname import set_nickname

path = 'set_nickname'


@pytest.fixture(autouse=True)
def client_notifier():
  with patch(f'{path}.client_notifier') as mock:
    yield mock


@pytest.fixture(autouse=True)
def connection_dao():
  with patch(f'{path}.connection_dao') as mock:
    yield mock 


def test_set_nickname(client_notifier, connection_dao):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id', modified_action=ConnectionAction.CREATE_CONNECTION)
  connection_dao.is_valid_nickname.return_value = True

  set_nickname({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
    'body': json.dumps({'data': {'nickname': 'nick_name'}})
  }, None)

  assert connection_dao.set.call_args.args[0].nickname == 'nick_name'
  assert connection_dao.set.call_args.args[0].modified_action == ConnectionAction.SET_NICKNAME
  client_notifier.send_notification.assert_called_once()


def test_set_nickname_invalid(client_notifier, connection_dao):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id', modified_action=ConnectionAction.CREATE_CONNECTION)
  connection_dao.is_valid_nickname.return_value = False

  set_nickname({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
    'body': json.dumps({'data': {'nickname': 'nick_name'}})
  }, None)

  assert not connection_dao.set.called
  client_notifier.send_notification.assert_called_once()
  