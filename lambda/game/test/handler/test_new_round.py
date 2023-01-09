import pytest
from unittest.mock import patch

from model import ConnectionAction, ConnectionItem, GameAction, GameState, Player, RollResultNote
from new_round import new_round

path = 'new_round'


@pytest.fixture(autouse=True)
def client_notifier():
  with patch(f'{path}.client_notifier') as mock:
    yield mock


@pytest.fixture(autouse=True)
def connection_dao():
  with patch(f'{path}.connection_dao') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def game_dao():
  with patch(f'{path}.game_dao') as mock:
    yield mock 


def test_new_round(connection_dao, game_dao, client_notifier):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id', game_id='ABCD', modified_action=ConnectionAction.CREATE_CONNECTION)
  game_dao.get.return_value = GameState(
    id='ABCD',
    mr_eleven='',
    round_id=0,
    round_finished=True,
    players=[Player(id=None, account_id=None, nickname=None, win_counter=None, finished=None, outcome=None, rolls=None)],
    modified_action=GameAction.CREATE_GAME,
    modified_by='nick',
  )

  new_round({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
  }, None)

  new_state = game_dao.set.call_args.args[0]
  assert new_state.round_id == 1
  assert not new_state.round_finished
  assert new_state.modified_action == GameAction.NEW_ROUND
  assert new_state.modified_by == 'nicks_connection_id'
  assert new_state.players[0].finished == False
  assert new_state.players[0].outcome == RollResultNote.NONE
  assert new_state.players[0].rolls == []
  client_notifier.send_game_state_update.assert_called_once()
