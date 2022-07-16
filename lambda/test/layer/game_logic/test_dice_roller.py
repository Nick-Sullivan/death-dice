# import os
# import pytest
# import sys

# sys.path.append(os.path.abspath('./lambda/src/python'))
# from model.dice import Roll, D4, D6, D8, D10, D12, D20, D10Percentile
# from game_logic.dice_roller import DiceRoller


# class TestDiceRoller:

#   @pytest.fixture
#   def obj(self):
#     yield DiceRoller()

#   @pytest.mark.parametrize('prev_rolls, win_counter, expected', [
#     pytest.param(
#       [],
#       0,
#       [D6, D6],
#       id='first roll',
#     ),
#     pytest.param(
#       [],
#       4,
#       [D6, D6, D4],
#       id='first roll with death dice',
#     ),
#     pytest.param(
#       [Roll([D6(), D6()])],
#       0,
#       [D6],
#       id='second roll',
#     ),
#     pytest.param(
#       [Roll([D6(), D6(), D12()])],
#       12,
#       [D6],
#       id='second roll with death dice',
#     ),
#   ])
#   def test_roll(self, obj, prev_rolls, win_counter, expected):
#     result = obj.roll(prev_rolls, win_counter, 'Nick')
#     assert len(result.dice) == len(expected)
#     assert all([isinstance(r, e) for r, e in zip(result.dice, expected)])

#   def test_roll_special_name(self, obj):
#     result = obj.roll([Roll([D6(), D6(), D6()])], 0, 'ABOVE_AVERAGE_JOE')
#     assert result.values[0] == 5
