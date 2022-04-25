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
  result = calculate_roll_results(rolls)
  assert expected == result

