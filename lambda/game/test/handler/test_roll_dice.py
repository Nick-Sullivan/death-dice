import pytest
from unittest.mock import patch

from model import ConnectionAction, ConnectionItem, D6, GameAction, GameState, Player, Roll, RollResult, RollResultNote, RollResultType
from roll_dice import roll_dice

path = 'roll_dice'


@pytest.fixture(autouse=True)
def calculate_turn_results():
  with patch(f'{path}.calculate_turn_results') as mock:
    mock.side_effect = lambda x: x
    yield mock 


@pytest.fixture(autouse=True)
def client_notifier():
  with patch(f'{path}.client_notifier') as mock:
    yield mock


@pytest.fixture(autouse=True)
def connection_dao():
  with patch(f'{path}.connection_dao') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def dice_roller():
  with patch(f'{path}.DiceRoller') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def game_dao():
  with patch(f'{path}.game_dao') as mock:
    yield mock 


@pytest.fixture(autouse=True)
def individual_roll_judge():
  with patch(f'{path}.IndividualRollJudge') as mock:
    yield mock 



def test_roll_dice(client_notifier, connection_dao, dice_roller, game_dao, individual_roll_judge):
  connection_dao.get.return_value = ConnectionItem(id='nicks_connection_id', game_id='ABCD', modified_action=ConnectionAction.CREATE_CONNECTION)
  game_dao.get.return_value = GameState(
    id='ABCD',
    mr_eleven='', 
    round_id=0,
    round_finished=True,
    players=[Player(
      id='nicks_connection_id',
      nickname=None,
      win_counter=None,
      finished=None,
      outcome=None,
      rolls=[Roll([D6(3)])]
    )],
    modified_action=GameAction.NEW_ROUND,
    modified_by='nick',
  )
  dice_roller.roll.return_value = Roll([D6(3), D6(3)])
  individual_roll_judge.calculate_result.return_value = RollResult(RollResultNote.POOL, RollResultType.LOSER, turn_finished=True)

  roll_dice({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
  }, None)

  new_state = game_dao.set.call_args.args[0]
  assert new_state.modified_action == GameAction.ROLL_DICE
  assert new_state.modified_by == 'nicks_connection_id'
  assert new_state.players[0].finished == True
  assert new_state.players[0].outcome == RollResultNote.POOL
  assert len(new_state.players[0].rolls) == 2
  client_notifier.send_game_state_update.assert_called_once()
