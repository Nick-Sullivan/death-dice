"""Models representing items stored in the Connection database"""

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dataclasses import dataclass, asdict
from datetime import datetime
from dateutil import parser
from enum import Enum


class ConnectionAction(Enum):
  CREATE_CONNECTION = 'CREATE_CONNECTION'
  SET_NICKNAME = 'SET_NICKNAME'
  JOIN_GAME = 'JOIN_GAME'


@dataclass
class ConnectionItem:
  id: str
  last_action: ConnectionAction
  nickname: str = None
  account_id: str = None
  game_id: str = None
  version: int = None
  created_on: datetime = None
  table: str = 'Connection'

  @staticmethod
  def serialise(obj):
    serialiser = TypeSerializer()
    item_dict = asdict(obj)

    # Enums
    item_dict['last_action'] = item_dict['last_action'].value

    # Datetimes
    item_dict['created_on'] = str(item_dict['created_on'])

    return serialiser.serialize(item_dict)['M']

  @staticmethod
  def deserialise(items):
    deserialiser = TypeDeserializer()
    item_dict = deserialiser.deserialize({'M': items})

    # Enums
    item_dict['last_action'] = ConnectionAction(item_dict['last_action'])

    # Datetimes
    item_dict['created_on'] = parser.parse(item_dict['created_on'])

    return ConnectionItem(**item_dict)
