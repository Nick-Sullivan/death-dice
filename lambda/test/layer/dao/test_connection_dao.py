
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from model import ConnectionItem
from dao import ConnectionDao, ConnectionNotFoundException

path = 'dao.connection_dao'


class TestConnectionDao:

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
    dao = ConnectionDao()
    with patch.object(dao, 'client'):
      yield dao

  def test_init(self, obj):
    assert isinstance(obj, ConnectionDao)

  def test_create(self, obj):
    obj.create(ConnectionItem(id='test'))
    obj.client.put_item.assert_called_once_with(**{
      'TableName': 'DeathDiceStage',
      'Item': {
        'id': {'S': 'test'},
        'nickname': {'NULL': True},
        'game_id': {'NULL': True},
        'version': {'N': '0'},
        'created_on': {'S': '2022-01-01 00:00:00+00:00'},
      },
      'ConditionExpression': 'attribute_not_exists(id)',
    })
  
  def test_get(self, obj, datetime_mock):
    obj.client.get_item.return_value = {
      'Item': ConnectionItem.serialise(
        ConnectionItem(
          id='test',
          created_on=datetime_mock.now()
        )
      )
    }
    item = obj.get('test')
    assert isinstance(item, ConnectionItem)
    assert item.id == 'test'
    obj.client.get_item.assert_called_once_with(**{
      'TableName': 'DeathDiceStage',
      'Key': {'id': {'S': 'test'}},
    })
  
  def test_get_not_found(self, obj, datetime_mock):
    obj.client.get_item.return_value = {}
    with pytest.raises(ConnectionNotFoundException):
      obj.get('id')

  def test_set(self, obj, transaction, datetime_mock):
    obj.set(ConnectionItem(id='id', game_id='game_id', version=2, created_on=datetime_mock.now()), transaction)

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'DeathDiceStage',
        'Item': {
          'id': {'S': 'id'},
          'nickname': {'NULL': True},
          'game_id': {'S': 'game_id'},
          'version': {'N': '3'},
          'created_on': {'S': '2022-01-01 00:00:00+00:00'},
        },
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': '2'}},
      }
    })

  def test_delete(self, obj, transaction):
    obj.delete(ConnectionItem(id="id", game_id="game_id", version=2), transaction)
    transaction.write.assert_called_once_with({
      'Delete': {
        'TableName': 'DeathDiceStage',
        'Key': {'id': {'S': 'id'}},
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': '2'}
        }
      }
    })
