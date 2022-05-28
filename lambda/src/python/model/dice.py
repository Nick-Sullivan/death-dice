"""Models representing physical dice, for use in rolling logic"""

import json
from random import randint
from typing import List


class Roll:
  """A list of Dice, with helper functions"""

  def __init__(self, dice=None):
    self.dice = [] if dice is None else dice
    assert(isinstance(self.dice, List))
    for d in self.dice:
      assert(isinstance(d, Dice))

  @classmethod
  def from_json(cls, json_str):
    dice_lookup = {cls.id: cls for cls in Dice.__subclasses__()} 

    dice = [
      dice_lookup[d['id']](value=d['value'])
      for d in json.loads(json_str)
    ]
    return Roll(dice)
  
  def to_json(self):
    return json.dumps([
      {'id': d.id, 'value': d.value} for d in self.dice
    ])

  def append(self, dice):
    assert(isinstance(dice, Dice))
    self.dice.append(dice)
  
  @property
  def values(self):
    return [d.value for d in self.dice]

  def __add__(self, other):
    assert(isinstance(other, Roll))
    return Roll(self.dice + other.dice)


class Dice:
  """Base class of a physical dice, a list of possible options, and each instance randomly selections one"""
  id = None
  options = None

  def __init__(self, value=None):
    assert(isinstance(self.id, str))
    assert(isinstance(self.options, list))
    self.value = self.roll() if value is None else value
    assert(self.value in self.options)

  @classmethod
  def roll(cls):
    index = randint(0, len(cls.options)-1)
    return cls.options[index]


class D4(Dice):
  id = 'D4'
  options = list(range(1, 5))


class D6(Dice):
  id = 'D6'
  options = list(range(1, 7))


class D8(Dice):
  id = 'D8'
  options = list(range(1, 9))


class D10(Dice):
  id = 'D10'
  options = list(range(0, 10))


class D12(Dice):
  id = 'D12'
  options = list(range(1, 13))


class D20(Dice):
  id = 'D20'
  options = list(range(1, 21))


class D10Percentile(Dice):
  id = 'D10Percentile'
  options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
