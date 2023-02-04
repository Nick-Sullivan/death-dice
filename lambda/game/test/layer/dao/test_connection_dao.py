
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from model import ConnectionAction, ConnectionItem
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
    obj.create(ConnectionItem(id='test', modified_action=ConnectionAction.CREATE_CONNECTION))
    obj.client.put_item.assert_called_once_with(**{
      'TableName': 'DeathDiceStage',
      'Item': {
        'id': {'S': 'test'},
        'nickname': {'NULL': True},
        'account_id': {'NULL': True},
        'game_id': {'NULL': True},
        'modified_action': {'S': 'CREATE_CONNECTION'},
        'version': {'N': '0'},
        'modified_at': {'S': '2022-01-01 00:00:00.000000'},
        'table': {'S': 'Connection'},
      },
      'ConditionExpression': 'attribute_not_exists(id)',
    })
  
  def test_get(self, obj, datetime_mock):
    obj.client.get_item.return_value = {
      'Item': ConnectionItem.serialise(
        ConnectionItem(
          id='test',
          modified_at=datetime_mock.now(),
          modified_action=ConnectionAction.SET_NICKNAME,
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
    obj.set(
      ConnectionItem(
        id='id',
        modified_action=ConnectionAction.SET_NICKNAME,
        account_id='account_id',
        game_id='game_id',
        version=2,
        modified_at=datetime_mock.now()
      ),
      transaction,
    )

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'DeathDiceStage',
        'Item': {
          'id': {'S': 'id'},
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
    obj.delete(ConnectionItem(id="id", game_id="game_id", version=2, modified_action=ConnectionAction.SET_NICKNAME), transaction)
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

  @pytest.mark.parametrize('name, expected', [
    pytest.param('Roib', True, id='normal'),
    pytest.param('', False, id='too short'),
    pytest.param('1234567891011121314151617', False, id='too long'),
    pytest.param('Mr Eleven', False, id='protected word'),
    pytest.param('Mr Eleven ', False, id='protected word with space'),
  ])
  def test_is_valid_nickname(self, obj, name, expected):
    assert obj.is_valid_nickname(name) == expected
