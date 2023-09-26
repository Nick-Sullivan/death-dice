
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from domain_models import D6, ConnectionStatus, GameAction, GameState, Player, Roll, RollResultNote
from infrastructure.cloud.game_store import GameNotFoundException, GameStore

path = 'infrastructure.cloud.game_store'


class TestGameStore:

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
    dao = GameStore(MagicMock(), 'MockTable')
    with patch.object(dao, 'client'):
      yield dao

  def test_init(self, obj):
    assert isinstance(obj, GameStore)

  def test_create(self, obj, transaction):
    game = GameState(
      id='test', 
      mr_eleven='nick',
      round_id=0,
      round_finished=False,
      modified_action=GameAction.CREATE_GAME,
      modified_by='nick',
      players=[
        Player(
          id='pid',
          account_id='account',
          nickname='nick',
          win_counter=1,
          finished=True,
          outcome=RollResultNote.DUAL_WIELD,
          rolls=[
            Roll([D6(4)])
          ],
          connection_status=ConnectionStatus.CONNECTED,
        )
      ],
      spectators=[],
    )
    obj.create(game, transaction)

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'MockTable',
        'Item': {
          'id': {'S': 'test'},
          'mr_eleven': {'S': 'nick'},
          'round_id': {'N': '0'},
          'round_finished': {'BOOL': False},
          'players': {'L': [{'M': {
            'id': {'S': 'pid'},
            'account_id': {'S': 'account'},
            'nickname': {'S': 'nick'},
            'win_counter': {'N': '1'},
            'finished': {'BOOL': True},
            'outcome': {'S': 'DUAL_WIELD'},
            'connection_status': {'S': 'CONNECTED'},
            'rolls': {'L': [{'M': {
              'dice': {'L': [{'M': {
                'id': {'S': 'D6'},
                'value': {'N': '4'},
                'is_death_dice': {'BOOL': False}
              }}]}
            }}]}
          }}]},
          'spectators': {'L': []},
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
          round_id=0,
          round_finished=None,
          modified_action=GameAction.CREATE_GAME,
          modified_by='nick',
          players=[],
          spectators=[],
          modified_at=datetime_mock.now(),
          version=2,
        )
      )
    }
    item = obj.get('test')
    assert isinstance(item, GameState)
    assert item.id == 'test'
    obj.client.get_item.assert_called_once_with(**{
      'TableName': 'MockTable',
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
      round_id=0,
      round_finished=False,
      modified_at=datetime_mock.now(),
      modified_action=GameAction.CREATE_GAME,
      modified_by='nick',
      players=[
        Player(
          id='pid',
          account_id='account',
          nickname='nick',
          win_counter=1,
          finished=True,
          outcome=RollResultNote.DUAL_WIELD,
          rolls=[
            Roll([D6(4)])
          ],
          connection_status=ConnectionStatus.CONNECTED,
        )
      ],
      spectators=[],
    )
    obj.set(game, transaction)

    transaction.write.assert_called_once_with({
      'Put': {
        'TableName': 'MockTable',
        'Item': {
          'id': {'S': 'test'},
          'mr_eleven': {'S': 'nick'},
          'round_id': {'N': '0'},
          'round_finished': {'BOOL': False},
          'players': {'L': [{'M': {
            'id': {'S': 'pid'},
            'account_id': {'S': 'account'},
            'nickname': {'S': 'nick'},
            'win_counter': {'N': '1'},
            'finished': {'BOOL': True},
            'outcome': {'S': 'DUAL_WIELD'},
            'connection_status': {'S': 'CONNECTED'},
            'rolls': {'L': [{'M': {
              'dice': {'L': [{'M': {
                'id': {'S': 'D6'},
                'value': {'N': '4'},
                'is_death_dice': {'BOOL': False}
              }}]}
            }}]}
          }}]},
          'spectators': {'L': []},
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
      round_id=0,
      round_finished=None,
      modified_action=GameAction.NEW_ROUND,
      modified_by='nick',
      players=[],
      spectators=[],
      version=2,
    )

    obj.delete(game, transaction)

    transaction.write.assert_called_once_with({
      'Delete': {
        'TableName': 'MockTable',
        'Key': {'id': {'S': 'test'}},
        'ConditionExpression': 'attribute_exists(id) AND version = :v',
        'ExpressionAttributeValues': {
          ':v': {'N': '2'}
        }
      }
    })
