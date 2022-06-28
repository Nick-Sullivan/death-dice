
from dataclasses import dataclass
from enum import Enum


class RollResultNote(Enum):
  NONE = ''
  DUAL_WIELD = 'DUAL_WIELD'
  HEAD_ON_TABLE = 'HEAD_ON_TABLE'
  FINISH_DRINK = 'FINISH_DRINK'
  POOL = 'POOL'
  SIP_DRINK = 'SIP_DRINK'
  SHOWER = 'SHOWER'
  THREE_WAY_TIE = 'THREE_WAY_TIE'
  TIE = 'TIE'
  WINNER = 'WINNER'
  WISH_PURCHASE = 'WISH_PURCHASE'


class RollResultType(Enum):
  NONE = 0
  LOSER = 1
  NO_CHANGE = 2
  WINNER = 3


@dataclass
class RollResult:
  note: RollResultNote
  type: RollResultType
  turn_finished: bool