


import os
import pytest
import sys
sys.path.append(os.path.abspath('./lambda/src/python'))
from player_dao import PlayerAttribute, PlayerDao


class TestPlayerAttribute:

  def test_init(self):
    a = PlayerAttribute.ID

class TestPlayerDao:

  def test_init(self):
    a = PlayerDao()