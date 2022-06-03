import pytest
import os
import pytest
import sys
from botocore.exceptions import ClientError
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath('./lambda/src/python'))
from client_notifier import ClientNotifier


class TestClientNotifier:
  
  @pytest.fixture(scope='function')
  def obj(self):
    with ExitStack() as stack:
      stack.enter_context(patch.object(ClientNotifier, 'gatewayapi'))
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
