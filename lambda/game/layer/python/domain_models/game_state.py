"""Models representing items stored in the Game database"""

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import List

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dateutil import parser

from .dice import Dice
from .roll_result import RollResultNote


class ConnectionStatus(Enum):
    CONNECTED = 'CONNECTED'
    PENDING_TIMEOUT = 'PENDING_TIMEOUT'


class GameAction(Enum):
    CREATE_GAME = 'CREATE_GAME'
    JOIN_GAME = 'JOIN_GAME'
    LEAVE_GAME = 'LEAVE_GAME'
    NEW_ROUND = 'NEW_ROUND'
    ROLL_DICE = 'ROLL_DICE'
    START_SPECTATING = 'START_SPECTATING'
    STOP_SPECTATING = 'STOP_SPECTATING'


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
  account_id: str
  nickname: str
  win_counter: int
  finished: bool
  outcome: RollResultNote
  rolls: List[Roll]
  connection_status: ConnectionStatus


@dataclass
class Spectator:
  id: str
  account_id: str
  nickname: str


@dataclass
class GameState:
  id: str
  mr_eleven: str
  players: List[Player]
  spectators: List[Spectator]
  round_id: int
  round_finished: bool
  modified_action: GameAction
  modified_by: str
  modified_at: datetime = None
  table: str = 'Game'
  version: int = None

  @staticmethod
  def serialise(obj):
    serialiser = TypeSerializer()

    # Enums
    game_dict = asdict(obj)
    for p in game_dict['players']:
      p['outcome'] = p['outcome'].value
      p['connection_status'] = p['connection_status'].value
    
    game_dict['modified_action'] = game_dict['modified_action'].value
    
    # Datetimes
    game_dict['modified_at'] = game_dict['modified_at'].strftime('%Y-%m-%d %H:%M:%S.%f')

    return serialiser.serialize(game_dict)['M']

  @staticmethod
  def deserialise(items):
    deserialiser = TypeDeserializer()

    game_dict = deserialiser.deserialize({'M': items})

    # Enums
    for p in game_dict['players']:
      p['outcome'] = RollResultNote(p['outcome'])
      p['connection_status'] = ConnectionStatus(p['connection_status'])
    
    game_dict['modified_action'] = GameAction(game_dict['modified_action'])

    # Datetimes
    game_dict['modified_at'] = parser.parse(game_dict['modified_at'])

    # Decimals
    game_dict['version'] = int(game_dict['version'])
    for p in game_dict['players']:
      p['win_counter'] = int(p['win_counter'])
      for r in p['rolls']:
        for d in r['dice']:
          d['value'] = int(d['value'])

    game = GameState(**game_dict)
    game.players = [Player(**p) for p in game.players]
    game.spectators = [Spectator(**s) for s in game.spectators]
    for player in game.players:
      player.rolls = [Roll(**r) for r in player.rolls]
      for roll in player.rolls:
        roll.dice = [Dice(**d) for d in roll.dice]
        
    return game
