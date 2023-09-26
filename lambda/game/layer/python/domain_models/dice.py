"""Models representing physical dice, for use in rolling logic"""

from dataclasses import dataclass
from random import randint
from typing import List


@dataclass
class Dice:
  id: str
  value: int
  is_death_dice: bool


class DiceFactory:
  """Inherited by specific dice (D4, D6 etc), instantiating creates a Dice object"""
  id = None
  options = None

  def __new__(cls, value=None, is_death_dice=False):
    assert isinstance(cls.id, str)
    value = cls.roll() if value is None else value
    assert value in cls.options
    return Dice(id=cls.id, value=value, is_death_dice=is_death_dice)

  @classmethod
  def roll(cls):
    assert isinstance(cls.options, List)
    index = randint(0, len(cls.options)-1)
    return cls.options[index]


class D4(DiceFactory):
  id = 'D4'
  options = list(range(1, 5))


class D6(DiceFactory):
  id = 'D6'
  options = list(range(1, 7))


class D8(DiceFactory):
  id = 'D8'
  options = list(range(1, 9))


class D10(DiceFactory):
  id = 'D10'
  options = list(range(0, 10))


class D12(DiceFactory):
  id = 'D12'
  options = list(range(1, 13))


class D20(DiceFactory):
  id = 'D20'
  options = list(range(1, 21))


class D10Percentile(DiceFactory):
  id = 'D10Percentile'
  options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
