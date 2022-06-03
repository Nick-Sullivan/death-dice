"""Models representing items stored in the Game database"""

from dataclasses import dataclass
from enum import Enum
from model.dynamodb_item import DynamodbItem
from typing import List


class ItemType(Enum):
  GAME = 'GAME'
  PLAYER = 'PLAYER'
  ROLL = 'ROLL'


@dataclass
class ConnectionItem(DynamodbItem):
  nickname: str = None


@dataclass
class GameItem(DynamodbItem):
  item_type: str = ItemType.GAME.value
  mr_eleven: str = None
  round_finished: bool = None


@dataclass
class PlayerItem(DynamodbItem):
  item_type: str = ItemType.PLAYER.value
  nickname: str = None
  win_counter: int = None
  finished: bool = None
  outcome: str = None


@dataclass
class RollItem(DynamodbItem):
  item_type: str = ItemType.ROLL.value
  player_id: str = None
  dice: str = None


@dataclass
class GameState:
  game : GameItem
  players : List[PlayerItem]
  rolls: List[RollItem]

  def flatten(self):
    flat = self.players + self.rolls
    if self.game is not None:
      flat += [self.game]
    return flat


def lookup_item_class(item_type):
  if item_type == ItemType.GAME:
    return GameItem
  if item_type == ItemType.PLAYER:
    return PlayerItem
  if item_type == ItemType.ROLL:
    return RollItem
  raise NotImplementedError()