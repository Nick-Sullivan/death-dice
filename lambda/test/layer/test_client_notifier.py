import os
import pytest
from botocore.exceptions import ClientError
from unittest.mock import MagicMock, patch

from client_interactor import ClientNotifier


class TestClientNotifier:
  
  @pytest.fixture(autouse=True)
  def mock_env_vars(self):
    with patch.dict(os.environ, {"GATEWAY_URL": "FAKE_URL"}):
      yield

  @pytest.fixture(scope='function')
  def obj(self):
    with patch('client_interactor.boto3'):
      yield ClientNotifier()

  def test_get_connection_id(self):
    assert ClientNotifier.get_connection_id('hi') == 'hi'

  def test_send_notification(self, obj):
    obj.send_notification(['player_id'], 'data')
    obj.gatewayapi.post_to_connection.assert_called_once_with(
      ConnectionId='player_id',
      Data='"data"',
    )
  
  def test_send_notification_gone(self, obj):
    obj.gatewayapi.post_to_connection = MagicMock(side_effect=self.fake_client_error_gone)
    obj.send_notification(['player_id'], 'data')

  def fake_client_error_gone(self, *args, **kwargs):
    raise ClientError(
      error_response={'Error': {'Code': 'GoneException'}},
      operation_name=''
    )

  def test_send_notification_error(self, obj):
    obj.gatewayapi.post_to_connection = MagicMock(side_effect=self.fake_client_error_other)
    with pytest.raises(ClientError):
      obj.send_notification(['player_id'], 'data')
  
  def fake_client_error_other(self, *args, **kwargs):
    raise ClientError(
      error_response={'Error': {'Code': 'SomethingElse'}},
      operation_name=''
    )
