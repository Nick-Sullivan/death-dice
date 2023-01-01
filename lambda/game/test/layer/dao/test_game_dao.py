
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from model import D6, GameAction, GameState, Player, Roll, RollResultNote
from dao import GameDao, GameNotFoundException

path = 'dao.game_dao'


class TestGameDao:

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
    dao = GameDao()
    with patch.object(dao, 'client'):
      yield dao

  def test_init(self, obj):
    assert isinstance(obj, GameDao)

  def test_create(self, obj, transaction):
    game = GameState(
      id='test', 
      mr_eleven='nick',
      round_finished=False,
      modified_action=GameAction.CREATE_GAME,
      modified_by='nick',
      players=[
        Player(
          id='pid',
          nickname='nick',
          win_counter=1,
          finished=True,
          outcome=RollResultNote.DUAL_WIELD,
          rolls=[
            Roll([D6(4)])
          ]
        )
      ]
    )
    obj.create(game, transaction)

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'DeathDiceStage',
        'Item': {
          'id': {'S': 'test'},
          'mr_eleven': {'S': 'nick'},
          'round_finished': {'BOOL': False},
          'players': {'L': [{'M': {
            'id': {'S': 'pid'},
            'nickname': {'S': 'nick'},
            'win_counter': {'N': '1'},
            'finished': {'BOOL': True},
            'outcome': {'S': 'DUAL_WIELD'},
            'rolls': {'L': [{'M': {
              'dice': {'L': [{'M': {
                'id': {'S': 'D6'},
                'value': {'N': '4'}
              }}]}
            }}]}
          }}]},
          'version': {'N': '0'},
          'modified_at': {'S': '2022-01-01 00:00:00.000000'},
          'modified_action': {'S': 'CREATE_GAME'},
          'modified_by': {'S': 'nick'},
          'table': {'S': 'Game'},
        },
        'ConditionExpression': 'attribute_not_exists(id)',
      }
    })
  
  def test_get(self, obj, datetime_mock):
    obj.client.get_item.return_value = {
      'Item': GameState.serialise(
        GameState(
          id='test',
          mr_eleven=None,
          round_finished=None,
          modified_action=GameAction.CREATE_GAME,
          modified_by='nick',
          players=[],
          modified_at=datetime_mock.now(),
          version=2,
        )
      )
    }
    item = obj.get('test')
    assert isinstance(item, GameState)
    assert item.id == 'test'
    obj.client.get_item.assert_called_once_with(**{
      'TableName': 'DeathDiceStage',
      'Key': {'id': {'S': 'test'}},
    })
  
  def test_get_not_found(self, obj, datetime_mock):
    obj.client.get_item.return_value = {}
    with pytest.raises(GameNotFoundException):
      obj.get('ABCD')
    
    obj.client.get_item.return_value = {'Item': None}
    with pytest.raises(GameNotFoundException):
      obj.get('invalid-game-id')

  def test_set(self, obj, transaction, datetime_mock):
    game = GameState(
      id='test',
      version=2,
      mr_eleven='nick',
      round_finished=False,
      modified_at=datetime_mock.now(),
      modified_action=GameAction.CREATE_GAME,
      modified_by='nick',
      players=[
        Player(
          id='pid',
          nickname='nick',
          win_counter=1,
          finished=True,
          outcome=RollResultNote.DUAL_WIELD,
          rolls=[
            Roll([D6(4)])
          ]
        )
      ]
    )
    obj.set(game, transaction)

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'DeathDiceStage',
        'Item': {
          'id': {'S': 'test'},
          'mr_eleven': {'S': 'nick'},
          'round_finished': {'BOOL': False},
          'players': {'L': [{'M': {
            'id': {'S': 'pid'},
            'nickname': {'S': 'nick'},
            'win_counter': {'N': '1'},
            'finished': {'BOOL': True},
            'outcome': {'S': 'DUAL_WIELD'},
            'rolls': {'L': [{'M': {
              'dice': {'L': [{'M': {
                'id': {'S': 'D6'},
                'value': {'N': '4'}
              }}]}
            }}]}
          }}]},
          'version': {'N': '3'},
          'modified_at': {'S': '2022-01-01 00:00:00.000000'},
          'modified_action': {'S': 'CREATE_GAME'},
          'modified_by': {'S': 'nick'},
          'table': {'S': 'Game'},
        },
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {':v': {'N': '2'}},
      }
    })

  def test_delete(self, obj, transaction):
    game = GameState(
      id='test',
      mr_eleven=None,
      round_finished=None,
      modified_action=GameAction.NEW_ROUND,
      modified_by='nick',
      players=[],
      version=2,
    )

    obj.delete(game, transaction)

    transaction.write.assert_called_once_with({
      'Delete': {
        'TableName': 'DeathDiceStage',
        'Key': {'id': {'S': 'test'}},
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': '2'}
        }
      }
    })
