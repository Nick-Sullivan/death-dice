"""Models representing items stored in the Connection database"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dateutil import parser


class SessionAction(Enum):
  CREATE_CONNECTION = 'CREATE_CONNECTION'
  SET_NICKNAME = 'SET_NICKNAME'
  JOIN_GAME = 'JOIN_GAME'
  PENDING_TIMEOUT = 'PENDING_TIMEOUT'
  RECONNECTED = 'RECONNECTED'


@dataclass
class SessionItem:
  id: str
  connection_id: str
  modified_action: SessionAction
  modified_at: datetime = None
  account_id: str = None
  game_id: str = None
  nickname: str = None
  table: str = 'Connection'
  version: int = None

  @staticmethod
  def serialise(obj):
    serialiser = TypeSerializer()
    item_dict = asdict(obj)

    # Enums
    item_dict['modified_action'] = item_dict['modified_action'].value

    # Datetimes
    item_dict['modified_at'] = item_dict['modified_at'].strftime('%Y-%m-%d %H:%M:%S.%f')

    return serialiser.serialize(item_dict)['M']

  @staticmethod
  def deserialise(items):
    deserialiser = TypeDeserializer()
    item_dict = deserialiser.deserialize({'M': items})

    # Enums
    item_dict['modified_action'] = SessionAction(item_dict['modified_action'])

    # Datetimes
    item_dict['modified_at'] = parser.parse(item_dict['modified_at']).replace(tzinfo=timezone.utc)

    return SessionItem(**item_dict)
