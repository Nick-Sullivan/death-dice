"""Models representing items stored in the Connection database"""

from dataclasses import asdict, dataclass
from datetime import datetime

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dateutil import parser


@dataclass
class WebsocketConnectionItem:
  connection_id: str
  session_id: str
  modified_at: datetime = None
  version: int = None

  @staticmethod
  def serialise(obj):
    serialiser = TypeSerializer()
    item_dict = asdict(obj)

    # Datetimes
    item_dict['modified_at'] = item_dict['modified_at'].strftime('%Y-%m-%d %H:%M:%S.%f')

    return serialiser.serialize(item_dict)['M']

  @staticmethod
  def deserialise(items):
    deserialiser = TypeDeserializer()
    item_dict = deserialiser.deserialize({'M': items})

    # Datetimes
    item_dict['modified_at'] = parser.parse(item_dict['modified_at'])

    return WebsocketConnectionItem(**item_dict)
