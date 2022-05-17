import os
import pytest
import sys

sys.path.append(os.path.abspath('./lambda/src/python'))
from dice_models import Roll, D4, D6, D8, D10, D12, D20, D10Percentile


class TestRoll:

  def test_append(self):
    roll = Roll([D4(1)])
    roll.append(D6(2))
    assert roll.values == [1, 2]

  def test_add(self):
    result = Roll([D4(1)]) + Roll([D6(2)])
    assert isinstance(result, Roll)
    assert result.values == [1, 2]

  def test_serialise(self):
    roll = Roll([D4(1), D6(2)])
    serialised = roll.to_json()
    deserialised = Roll.from_json(serialised)
    assert deserialised.values == roll.values
