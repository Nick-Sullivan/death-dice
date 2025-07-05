import pytest
from domain_models import D4, D6, D12, Roll
from domain_models.commands import DecideDiceValuesCommand
from mediator import mediator

id = __name__

class TestDecideDiceValuesHandler:

    @pytest.mark.parametrize('prev_rolls, win_counter, expected', [
        pytest.param(
        [],
        0,
        [D6, D6],
        id='first roll',
        ),
        pytest.param(
        [],
        4,
        [D6, D6, D4],
        id='first roll with death dice',
        ),
        pytest.param(
        [Roll([D6(), D6()])],
        0,
        [D6],
        id='second roll',
        ),
        pytest.param(
        [Roll([D6(), D6(), D12()])],
        12,
        [D6],
        id='second roll with death dice',
        ),
    ])
    def test_it_uses_correct_dice(self, prev_rolls, win_counter, expected):
        result = mediator.send(DecideDiceValuesCommand(prev_rolls, win_counter, ''))
        assert len(result.dice) == len(expected)
        assert all([r.id == e.id for r, e in zip(result.dice, expected)])

    def test_it_is_consistent_with_special_names(self):
        result = mediator.send(DecideDiceValuesCommand([Roll([D6(), D6(), D6()])], 0, 'ABOVE_AVERAGE_JOE'))
        assert result.values[0] == 5
