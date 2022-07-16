"""Models representing items stored in the Game database"""

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dataclasses import dataclass, asdict
from datetime import datetime
from dateutil import parser
from typing import List

from model.dice import Dice
from model.roll_result import RollResultNote


@dataclass
class Roll:
  dice: List[Dice]
  
  @property
  def values(self) -> List[int]:
    return [d.value for d in self.dice]

  def __add__(self, other):
    assert(isinstance(other, Roll))
    return Roll(self.dice + other.dice)

  def to_json(self):
    return asdict(self)['dice']


@dataclass
class Player:
  id: str
  nickname: str
  win_counter: int
  finished: bool
  outcome: RollResultNote
  rolls: List[Roll]


@dataclass
class GameState:
  id: str
  mr_eleven: str
  round_finished: bool
  players: List[Player]
  version: int = None
  created_on: datetime = None

  @staticmethod
  def serialise(obj):
    serialiser = TypeSerializer()

    # Enums
    game_dict = asdict(obj)
    for p in game_dict['players']:
      p['outcome'] = p['outcome'].value
    
    # Datetimes
    game_dict['created_on'] = str(game_dict['created_on'])

    return serialiser.serialize(game_dict)['M']

  @staticmethod
  def deserialise(items):
    deserialiser = TypeDeserializer()

    game_dict = deserialiser.deserialize({'M': items})

    # Enums
    for p in game_dict['players']:
      p['outcome'] = RollResultNote(p['outcome'])

    # Datetimes
    game_dict['created_on'] = parser.parse(game_dict['created_on'])

    # Decimals
    game_dict['version'] = int(game_dict['version'])
    for p in game_dict['players']:
      p['win_counter'] = int(p['win_counter'])
      for r in p['rolls']:
        for d in r['dice']:
          d['value'] = int(d['value'])

    game = GameState(**game_dict)
    game.players = [Player(**p) for p in game.players]
    for player in game.players:
      player.rolls = [Roll(**r) for r in player.rolls]
      for roll in player.rolls:
        roll.dice = [Dice(**d) for d in roll.dice]
        
    return game
