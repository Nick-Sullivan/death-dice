import pytest
from botocore.exceptions import ClientError
from unittest.mock import MagicMock

from infrastructure.cloud.client_notifier import ClientNotifier


class TestClientNotifier:
  
  @pytest.fixture(scope='function')
  def websocket(self):
    return MagicMock()
  
  @pytest.fixture(scope='function')
  def obj(self, websocket):
    return ClientNotifier(websocket)

  def test_send_notification(self, obj, websocket):
    obj.send_notification(['player_id'], {'data': 'hi'})
    websocket.post_to_connection.assert_called_once_with(
      ConnectionId='player_id',
      Data='{"data": "hi"}',
    )
  
  def test_send_notification_gone_doesnt_error(self, obj, websocket):
    websocket.post_to_connection = MagicMock(side_effect=self.fake_client_error_gone)
    obj.send_notification(['player_id'], {'data': 'hi'})

  def fake_client_error_gone(self, *args, **kwargs):
    raise ClientError(
      error_response={'Error': {'Code': 'GoneException'}},
      operation_name=''
    )
