from dataclasses import dataclass, fields
from datetime import datetime


@dataclass
class DynamodbItem:
  """All fields must be optional, to support lazy reads from the database"""
  game_id: str = None
  id: str = None
  version: int = None
  created_on: datetime = None
  

  def to_query(self):
    response = {}
    for f in fields(self):

      value = getattr(self, f.name)
      if value is None:
        continue

      response[f.name] = self.python_to_dynamodb_type(f.type, value)

    return response

  @classmethod
  def from_query(cls, query):
    kwargs = {}
    for k, v in query.items():
      assert len(v) == 1
      type = list(v)[0]
      value = list(v.values())[0]

      if value is None:
        continue

      kwargs[k] = cls.dynamodb_type_to_python(type, value)

    return cls(**kwargs)

  @staticmethod
  def python_to_dynamodb_type(python_type, value):
    if python_type == str:
      return {'S': value}
    if python_type == int:
      return {'N': str(value)}
    if python_type == bool:
      return {'BOOL': value}
    if python_type == datetime:
      return {'S': str(value)}
    raise NotImplementedError()

  @staticmethod
  def dynamodb_type_to_python(dynamodb_type, value):
    if dynamodb_type == 'S':
      return value
    if dynamodb_type == 'N':
      return int(value)
    if dynamodb_type == 'BOOL':
      return bool(value)
    raise NotImplementedError()

  def update_from(self, other_obj):
    """Copies values from the given object, and uses them for our own values"""
    for field in fields(self):
      setattr(self, field.name, getattr(other_obj, field.name))
