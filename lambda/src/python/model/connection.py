"""Models representing items in the Connection database"""

from dataclasses import dataclass

from model.base import DynamodbItem


@dataclass
class ConnectionItem(DynamodbItem):
  nickname: str = None
