import os
import pytest
import sys
sys.path.append(os.path.abspath('./lambda/src/python'))
from dice_models import Roll, D4, D6, D8, D10, D12, D20, D10Percentile
from game_logic import RollResult, calculate_turn_results, _should_roll_another_dice


@pytest.mark.parametrize('initial_values, extra_values, expected', [
  pytest.param(
    [1, 2],
    [],
    False,
    id='no duplicates',
  ),
  pytest.param(
    [6, 6],
    [],
    True,
    id='duplicates on initial',
  ),
  pytest.param(
    [6, 2, 6],
    [],
    True,
    id='duplicates on initial w/ death dice',
  ),
  pytest.param(
    [6, 6, 6],
    [],
    True,
    id='triple on initial',
  ),
  pytest.param(
    [1, 1, 1],
    [],
    False,
    id='triple on initial hits cap',
  ),
  pytest.param(
    [6, 6],
    [6],
    True,
    id='extra throw match',
  ),
  pytest.param(
    [6, 2, 6],
    [6],
    True,
    id='extra throw match w/ death dice',
  ),
  pytest.param(
    [6, 2, 6],
    [2],
    False,
    id='extra throw no match w/ death dice',
  ),
  pytest.param(
    [6, 2, 6],
    [6, 6, 6, 6],
    False,
    id='extra throw hits cap',
  ),
])
def test__should_roll_another_dice(initial_values, extra_values, expected):
  initial_throw = Roll([D6(v) for v in initial_values])
  extra_throws = Roll([D6(v) for v in extra_values])
  result = _should_roll_another_dice(initial_throw, extra_throws)
  assert expected == result

@pytest.mark.parametrize('roll_values, expected', [
  pytest.param(
    {},
    {},
    id='empty',
  ),
  pytest.param(
    {'k': [1, 5]},
    {'k': RollResult.WINNER},
    id='solo winner',
  ),
  pytest.param(
    {'k': [1, 1, 6]},
    {'k': RollResult.SIP_DRINK},
    id='solo snake eyes safe',
  ),
  pytest.param(
    {'k': [1, 1, 1]},
    {'k': RollResult.FINISH_DRINK},
    id='solo snake eyes fail',
  ),
  pytest.param(
    {'k': [3, 3, 3]},
    {'k': RollResult.SHOWER},
    id='solo shower',
  ),
  pytest.param(
    {
      'a': [3, 2, 1],
      'b': [1, 2, 3],
    },
    {
      'a': RollResult.TIE,
      'b': RollResult.TIE,
    },
    id='duo tie',
  ),
])
def test_calculate_roll_results(roll_values, expected):
  rolls = {}
  for k, values in roll_values.items():
    rolls[k] = Roll([D6(v) for v in values]).to_json()

  result, _ = calculate_turn_results(rolls)
  assert expected == result

@pytest.mark.parametrize('roll_values, expected, expected_mr_eleven', [
  pytest.param(
    {
      'MrEleven': [6, 5],
      'Nick': [6, 6, 6, 5],
    },
    {
      'MrEleven': RollResult.WINNER,
      'Nick': RollResult.SIP_DRINK
    },
    'MrEleven',
    id='mr eleven wins with an 11',
  ),
  pytest.param(
    {
      'MrEleven': [3, 3, 5],
      'Nick': [6, 5],
    },
    {
      'MrEleven': RollResult.WINNER,
      'Nick': RollResult.WINNER
    },
    'MrEleven',
    id='other 11s dont lose',
  ),
  pytest.param(
    {
      'MrEleven': [6, 6, 4],
      'Nick': [6, 5],
    },
    {
      'MrEleven': RollResult.WINNER,
      'Nick': RollResult.SIP_DRINK
    },
    'Nick',
    id='mr eleven changes',
  ),
  pytest.param(
    {
      'MrEleven': [1, 2],
      'Nick': [1, 3],
    },
    {
      'MrEleven': RollResult.SIP_DRINK,
      'Nick': RollResult.WINNER
    },
    'MrEleven',
    id='mr eleven doesnt change',
  ),
])
def test_calculate_roll_results_mr_eleven(roll_values, expected, expected_mr_eleven):
  rolls = {}
  for k, values in roll_values.items():
    rolls[k] = Roll([D6(v) for v in values]).to_json()

  result, mr_eleven = calculate_turn_results(rolls, 'MrEleven')
  assert expected == result
  assert expected_mr_eleven == mr_eleven

# TODO - roll results with death dice