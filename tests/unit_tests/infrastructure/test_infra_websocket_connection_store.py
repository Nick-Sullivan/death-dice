
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from domain_models import WebsocketConnectionItem
from infrastructure.cloud.websocket_connection_store import WebsocketConnectionStore, \
    WebsocketConnectionNotFoundException

path = 'infrastructure.cloud.websocket_connection_store'


class TestWebsocketConnectionStore:

  @pytest.fixture(autouse=True)
  def datetime_mock(self):
    with patch(f'{path}.datetime') as mock:
      mock.now.return_value = datetime(2022, 1, 1, tzinfo=timezone.utc)
      yield mock
    
  @pytest.fixture
  def transaction(self):
    return MagicMock()

  @pytest.fixture
  def obj(self):
    dao = WebsocketConnectionStore(MagicMock(), 'MockTable')
    with patch.object(dao, 'client'):
      yield dao

  def test_init(self, obj):
    assert isinstance(obj, WebsocketConnectionStore)

  def test_create(self, obj, transaction):
    obj.create(WebsocketConnectionItem(connection_id='c', session_id='s'), transaction)
    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'MockTable',
        'Item': {
          'connection_id': {'S': 'c'},
          'session_id': {'S': 's'},
          'modified_at': {'S': '2022-01-01 00:00:00.000000'},
          'version': {'N': '0'},
        },
        'ConditionExpression': 'attribute_not_exists(id)',
      }
    })
  
  def test_get(self, obj, datetime_mock):
    obj.client.get_item.return_value = {
      'Item': WebsocketConnectionItem.serialise(
        WebsocketConnectionItem(
          connection_id='c',
          session_id='s',
          modified_at=datetime_mock.now(),
        )
      )
    }
    item = obj.get('c')
    assert isinstance(item, WebsocketConnectionItem)
    assert item.connection_id == 'c'
    obj.client.get_item.assert_called_once_with(**{
      'TableName': 'MockTable',
      'Key': {'connection_id': {'S': 'c'}},
    })
  
  def test_get_not_found(self, obj, datetime_mock):
    obj.client.get_item.return_value = {}
    with pytest.raises(WebsocketConnectionNotFoundException):
      obj.get('id')

  def test_set(self, obj, transaction, datetime_mock):
    obj.set(
      WebsocketConnectionItem(
        connection_id='c',
        session_id='s',
        modified_at=datetime_mock.now(),
        version=2,
      ),
      transaction,
    )

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'MockTable',
        'Item': {
          'connection_id': {'S': 'c'},
          'session_id': {'S': 's'},
          'modified_at': {'S': '2022-01-01 00:00:00.000000'},
          'version': {'N': '3'},
        },
        'ConditionExpression': 'attribute_exists(connection_id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': '2'}},
      }
    })

  def test_delete(self, obj, transaction):
    obj.delete(WebsocketConnectionItem(session_id='s', connection_id='c', version=2), transaction)
    transaction.write.assert_called_once_with({
      'Delete': {
        'TableName': 'MockTable',
        'Key': {'connection_id': {'S': 'c'}},
        'ConditionExpression': 'attribute_exists(connection_id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': '2'}
        }
      }
    })
