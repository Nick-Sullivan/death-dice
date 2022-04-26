import pytest
from src.python.game_logic import RollResult, calculate_roll_results


@pytest.mark.parametrize('rolls, expected', [
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
def test_calculate_roll_results(rolls, expected):
  result, _ = calculate_roll_results(rolls)
  assert expected == result

@pytest.mark.parametrize('rolls, expected, expected_mr_eleven', [
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
def test_calculate_roll_results_mr_eleven(rolls, expected, expected_mr_eleven):
  result, mr_eleven = calculate_roll_results(rolls, 'MrEleven')
  assert expected == result
  assert expected_mr_eleven == mr_eleven
