"""Models representing items stored in the Connection database"""

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dataclasses import dataclass, asdict
from datetime import datetime
from dateutil import parser


@dataclass
class ConnectionItem:
  id: str
  nickname: str = None
  game_id: str = None
  version: int = None
  created_on: datetime = None

  @staticmethod
  def serialise(obj):
    serialiser = TypeSerializer()
    item_dict = asdict(obj)
    item_dict['created_on'] = str(item_dict['created_on'])
    return serialiser.serialize(item_dict)['M']

  @staticmethod
  def deserialise(items):
    deserialiser = TypeDeserializer()
    item_dict = deserialiser.deserialize({'M': items})
    item_dict['created_on'] = parser.parse(item_dict['created_on'])
    return ConnectionItem(**item_dict)
