from unittest.mock import patch

from connect import connect
from model import ConnectionAction

path = 'connect'


@patch(f'{path}.connection_dao')
def test_connect(connection_dao):
  connect({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)

  connection_dao.create.assert_called_once()
  assert connection_dao.create.call_args.args[0].id == 'nicks_connection_id'
  assert connection_dao.create.call_args.args[0].last_action == ConnectionAction.CREATE_CONNECTION
