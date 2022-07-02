import os
import pytest
import sys

sys.path.append(os.path.abspath('./lambda/src/python'))
from model.dice import Roll, D4, D6, D8, D10, D12, D20, D10Percentile
from game_logic.roll_judge import IndividualRollJudge, GroupRollJudge
from model.roll_result import RollResult, RollResultNote, RollResultType


class TestIndividualRollJudge:

  @pytest.fixture
  def obj(self):
    yield IndividualRollJudge()

  @pytest.mark.parametrize('roll_values, expected', [
    pytest.param(
      [],
      RollResult(note=RollResultNote.NONE, type=RollResultType.NONE, turn_finished=False),
      id='no rolls',
    ),
    pytest.param(
      [[2, 2], [2]],
      RollResult(note=RollResultNote.NONE, type=RollResultType.NONE, turn_finished=False),
      id='turn not finished',
    ),
    pytest.param(
      [[1, 5]],
      RollResult(note=RollResultNote.NONE, type=RollResultType.NONE, turn_finished=True),
      id='turn finished, not enough info',
    ),
    pytest.param(
      [[1, 1], [2]],
      RollResult(note=RollResultNote.FINISH_DRINK, type=RollResultType.LOSER, turn_finished=True),
      id='snake eyes fail is instant lose',
    ),
    pytest.param(
      [[1, 1], [5]],
      RollResult(note=RollResultNote.SIP_DRINK, type=RollResultType.LOSER, turn_finished=True),
      id='snake eyes safe is instant lose',
    ),
    pytest.param(
      [[2, 2], [2], [2]],
      RollResult(note=RollResultNote.DUAL_WIELD, type=RollResultType.NONE, turn_finished=True),
      id='dual wield',
    ),
    pytest.param(
      [[3, 3], [3]],
      RollResult(note=RollResultNote.SHOWER, type=RollResultType.LOSER, turn_finished=True),
      id='shower is instant lose',
    ),
    pytest.param(
      [[4, 4], [4], [4]],
      RollResult(note=RollResultNote.HEAD_ON_TABLE, type=RollResultType.NONE, turn_finished=True),
      id='head on table',
    ),
    pytest.param(
      [[5, 5], [5], [5], [5]],
      RollResult(note=RollResultNote.WISH_PURCHASE, type=RollResultType.NONE, turn_finished=True),
      id='wish',
    ),
    pytest.param(
      [[6, 6], [6], [6], [6], [6]],
      RollResult(note=RollResultNote.POOL, type=RollResultType.LOSER, turn_finished=True),
      id='pool is instant lose',
    ),
    pytest.param(
      [[1, 1, 2]],
      RollResult(note=RollResultNote.NONE, type=RollResultType.NONE, turn_finished=False),
      id='snake eyes and extra with death dice',
    ),
    pytest.param(
      [[1, 1, 2], [1]],
      RollResult(note=RollResultNote.FINISH_DRINK, type=RollResultType.LOSER, turn_finished=True),
      id='snake eyes and extra with death dice, fail',
    ),
    pytest.param(
      [[1, 1, 1]],
      RollResult(note=RollResultNote.FINISH_DRINK, type=RollResultType.LOSER, turn_finished=True),
      id='snake eyes with death dice immediate fail',
    ),
  ])
  def test_calculate_result(self, obj, roll_values, expected):
    rolls = self._create_rolls_from_values(roll_values)
    result = obj.calculate_result(rolls, False)
    assert result.__dict__ == expected.__dict__

  @pytest.mark.parametrize('roll_values, expected', [
    pytest.param(
      [[1, 5]],
      RollResult(note=RollResultNote.NONE, type=RollResultType.NONE, turn_finished=True),
      id='normal roll',
    ),
    pytest.param(
      [[6, 5]],
      RollResult(note=RollResultNote.WINNER, type=RollResultType.WINNER, turn_finished=True),
      id='rolls 11',
    ),
  ])
  def test_calculate_result_mr_eleven(self, obj, roll_values, expected):
    rolls = self._create_rolls_from_values(roll_values)
    result = obj.calculate_result(rolls, True)
    assert result.__dict__ == expected.__dict__

  def _create_rolls_from_values(self, roll_values):
    rolls = []
    for roll in roll_values:
      rolls.append(Roll([D6(v) for v in roll]))

    return rolls


class TestGroupRollJudge:

  @pytest.mark.parametrize('player_roll_values, expected', [
    pytest.param(
      {},
      {},
      id='no players',
    ),
    pytest.param(
      {'A': [[1, 5]]},
      {'A': RollResult(RollResultNote.WINNER, RollResultType.WINNER, turn_finished=True)},
      id='solo player win',
    ),
    pytest.param(
      {'A': [[1, 1], [1]]},
      {'A': RollResult(RollResultNote.FINISH_DRINK, RollResultType.LOSER, turn_finished=True)},
      id='solo player lose',
    ),
    pytest.param(
      {
        'A': [[3, 1]],
        'B': [[1, 3]],
      },
      {
        'A': RollResult(RollResultNote.TIE, RollResultType.LOSER, turn_finished=True),
        'B': RollResult(RollResultNote.TIE, RollResultType.LOSER, turn_finished=True),
      },
      id='simple tie',
    ),
    pytest.param(
      {
        'A': [[2, 2], [2], [3]],
        'B': [[5, 4]],
      },
      {
        'A': RollResult(RollResultNote.TIE, RollResultType.LOSER, turn_finished=True),
        'B': RollResult(RollResultNote.TIE, RollResultType.LOSER, turn_finished=True),
      },
      id='complicated tie',
    ),
    pytest.param(
      {
        'A': [[2, 2], [2], [2]],
        'B': [[5, 3]],
      },
      {
        'A': RollResult(RollResultNote.DUAL_WIELD, RollResultType.LOSER, turn_finished=True),
        'B': RollResult(RollResultNote.TIE, RollResultType.LOSER, turn_finished=True),
      },
      id='tie with dual wield',
    ),
    pytest.param(
      {
        'A': [[2, 2], [2], [2]],
        'B': [[1, 3]],
      },
      {
        'A': RollResult(RollResultNote.DUAL_WIELD, RollResultType.WINNER, turn_finished=True),
        'B': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
      },
      id='win with dual wield',
    ),
    pytest.param(
      {
        'A': [[1, 1], [6]],
        'B': [[1, 2, 1], [6]],
      },
      {
        'A': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
        'B': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
      },
      id='duo both lose',
    ),
    pytest.param(
      {
        'A': [[1, 2]],
        'B': [[1, 1], [1]],
      },
      {
        'A': RollResult(RollResultNote.WINNER, RollResultType.WINNER, turn_finished=True),
        'B': RollResult(RollResultNote.FINISH_DRINK, RollResultType.LOSER, turn_finished=True),
      },
      id='duo snake eyes',
    ),
    pytest.param(
      {
        'A': [[3, 5]],
        'B': [[3, 5]],
        'C': [[5, 3]],
      },
      {
        'A': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
        'B': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
        'C': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
      },
      id='three way tie',
    ),
    pytest.param(
      {
        'A': [[4, 4], [4], [4]],
        'B': [[6, 6], [4]],
        'C': [[6, 6, 2], [2]],
      },
      {
        'A': RollResult(RollResultNote.HEAD_ON_TABLE, RollResultType.NO_CHANGE, turn_finished=False),
        'B': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
        'C': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
      },
      id='three way tie with head on table',
    ),
    pytest.param(
      {
        'A': [[4, 4], [4], [4], [4]],
        'B': [[6, 6], [4], [3]],
        'C': [[6, 6, 4], [3]],
      },
      {
        'A': RollResult(RollResultNote.HEAD_ON_TABLE, RollResultType.WINNER, turn_finished=True),
        'B': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
        'C': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
      },
      id='the roll after three way tie with head on table',
    ),
    pytest.param(
      {
        'A': [[3, 5]],
        'B': [[3, 5]],
        'C': [[5, 3]],
        'D': [[1, 1], [1]],
      },
      {
        'A': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
        'B': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
        'C': RollResult(RollResultNote.THREE_WAY_TIE, RollResultType.NO_CHANGE, turn_finished=False),
        'D': RollResult(RollResultNote.FINISH_DRINK, RollResultType.LOSER, turn_finished=True),
      },
      id='four players results in three way tie',
    ),
    pytest.param(
      {
        'A': [[6, 6], [3]],
        'MrEleven': [[6, 5]],
      },
      {
        'A': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
        'MrEleven': RollResult(RollResultNote.WINNER, RollResultType.WINNER, turn_finished=True),
      },
      id='mr eleven wins',
    ),
    pytest.param(
      {
        'A': [[6, 5]],
        'MrEleven': [[6, 5]],
      },
      {
        'A': RollResult(RollResultNote.WINNER, RollResultType.NO_CHANGE, turn_finished=True),
        'MrEleven': RollResult(RollResultNote.WINNER, RollResultType.WINNER, turn_finished=True),
      },
      id='matching mr eleven doesnt lose',
    ),
    pytest.param(
      {
        'A': [[6, 5]],
        'B': [[6, 6], [3]],
        'MrEleven': [[6, 5]],
      },
      {
        'A': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
        'B': RollResult(RollResultNote.SIP_DRINK, RollResultType.LOSER, turn_finished=True),
        'MrEleven': RollResult(RollResultNote.WINNER, RollResultType.WINNER, turn_finished=True),
      },
      id='matching mr eleven still loses if theres a higher value',
    ),
  ])
  def test_calculate_result(self, player_roll_values, expected):
    player_rolls = self._create_rolls_from_values(player_roll_values)

    judge = GroupRollJudge(player_rolls, 'MrEleven')

    result = judge.calculate_result()

    for player, expected_roll_result in expected.items():
      assert expected_roll_result.__dict__ == result[player].__dict__

  @pytest.mark.parametrize('player_roll_values, expected', [
    pytest.param(
      {
        'A': [[5, 6]],
      },
      'A',
      id='new mr eleven'
    ),
    pytest.param(
      {
        'A': [[5, 6]],
        'MrEleven': [[2, 3]],
      },
      'A',
      id='replacing mr eleven'
    ),
    pytest.param(
      {
        'A': [[5, 6]],
        'MrEleven': [[5, 6]],
      },
      'MrEleven',
      id='original mr eleven maintained'
    ),
    pytest.param(
      {
        'A': [[2, 3]],
        'MrEleven': [[1, 2]],
      },
      'MrEleven',
      id='nobody rolls 11'
    ),
  ])
  def test_calculate_new_mr_eleven(self, player_roll_values, expected):
    player_rolls = self._create_rolls_from_values(player_roll_values)

    judge = GroupRollJudge(player_rolls, 'MrEleven')

    result = judge.calculate_new_mr_eleven()
    assert expected == result

  def _create_rolls_from_values(self, player_roll_values):
    player_rolls = {}
    for player, roll_values in player_roll_values.items():
      player_rolls[player] = []
      for roll in roll_values:
        player_rolls[player].append(Roll([D6(v) for v in roll]))

    return player_rolls
  