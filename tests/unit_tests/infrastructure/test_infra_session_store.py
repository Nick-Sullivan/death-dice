
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from domain_models import SessionAction, SessionItem
from infrastructure.cloud.session_store import SessionNotFoundException, SessionStore

path = 'infrastructure.cloud.session_store'


class TestSessionStore:

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
    dao = SessionStore(MagicMock(), 'MockTable')
    with patch.object(dao, 'client'):
      yield dao

  def test_init(self, obj):
    assert isinstance(obj, SessionStore)

  def test_create(self, obj, transaction):
    obj.create(SessionItem(id='test', connection_id='c', modified_action=SessionAction.CREATE_CONNECTION), transaction)
    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'MockTable',
        'Item': {
          'id': {'S': 'test'},
          'connection_id': {'S': 'c'},
          'nickname': {'NULL': True},
          'account_id': {'NULL': True},
          'game_id': {'NULL': True},
          'modified_action': {'S': 'CREATE_CONNECTION'},
          'version': {'N': '0'},
          'modified_at': {'S': '2022-01-01 00:00:00.000000'},
          'table': {'S': 'Connection'},
        },
        'ConditionExpression': 'attribute_not_exists(id)',
      }
    })
  
  def test_get(self, obj, datetime_mock):
    obj.client.get_item.return_value = {
      'Item': SessionItem.serialise(
        SessionItem(
          id='test',
          connection_id='c',
          modified_at=datetime_mock.now(),
          modified_action=SessionAction.SET_NICKNAME,
        )
      )
    }
    item = obj.get('test')
    assert isinstance(item, SessionItem)
    assert item.id == 'test'
    assert item.modified_at.tzinfo == timezone.utc
    obj.client.get_item.assert_called_once_with(**{
      'TableName': 'MockTable',
      'Key': {'id': {'S': 'test'}},
    })
  
  def test_get_not_found(self, obj, datetime_mock):
    obj.client.get_item.return_value = {}
    with pytest.raises(SessionNotFoundException):
      obj.get('id')

  def test_set(self, obj, transaction, datetime_mock):
    obj.set(
        SessionItem(
            id='id',
            connection_id='c',
            modified_action=SessionAction.SET_NICKNAME,
            account_id='account_id',
            game_id='game_id',
            version=2,
            modified_at=datetime_mock.now()
        ),
        transaction,
    )

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'MockTable',
        'Item': {
          'id': {'S': 'id'},
          'connection_id': {'S': 'c'},
          'nickname': {'NULL': True},
          'account_id': {'S': 'account_id'},
          'game_id': {'S': 'game_id'},
          'modified_action': {'S': 'SET_NICKNAME'},
          'version': {'N': '3'},
          'modified_at': {'S': '2022-01-01 00:00:00.000000'},
          'table': {'S': 'Connection'},
        },
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': '2'}},
      }
    })

  def test_delete(self, obj, transaction):
    obj.delete(
        SessionItem(
            id="id",
            connection_id='c',
            game_id="game_id", 
            version=2, 
            modified_action=SessionAction.SET_NICKNAME
        ),
        transaction
    )
    transaction.write.assert_called_once_with({
      'Delete': {
        'TableName': 'MockTable',
        'Key': {'id': {'S': 'id'}},
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': '2'}
        }
      }
    })
