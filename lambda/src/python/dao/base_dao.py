from dataclasses import dataclass, fields


@dataclass
class DynamodbItem:
  """All fields must be optional, to support lazy reads from the database"""
  id: str = None

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

class BaseDao:
  
  table_name = None
  item_class = None

  def __init__(self):
      assert isinstance(self.table_name, str)
      assert issubclass(self.item_class, DynamodbItem)

  def create(self, connection, item):
    assert isinstance(item, self.item_class)
    connection.write({
      'Put': {
        'TableName': self.table_name,
        'Item': item.to_query(),
        'ConditionExpression': f'attribute_not_exists(id)',
      }
    })

  def delete(self, connection, id):
    assert isinstance(id, str)
    connection.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
        'ConditionExpression': f'attribute_exists(id)',
      }
    })
  
  def get(self, connection, id):
    assert isinstance(id, str)
    return connection.read({
      'Get': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
      }
    }, self.item_class)

  def set(self, connection, item):
    assert isinstance(item, self.item_class)
    assert item.id is not None

    query = item.to_query()

    expressions = []
    values = {}
    for i, (key, value) in enumerate(query.items()):
      if key == 'id':
        continue
      expressions.append(f'{key} = :{i}')
      values[f':{i}'] = value

    update_expression = f'SET ' + ', '.join(expressions)

    connection.write({
      'Update': {
        'TableName': self.table_name,
        'Key': {'id': {'S': item.id}},
        'ConditionExpression': f'attribute_exists(id)',
        'UpdateExpression': update_expression,
        "ExpressionAttributeValues": values,
      }
    })

  def exists(self, connection, id):
    return self.get(connection, id) != None

  def delete_if_attribute_has_value(self, connection, id, attribute, value):
    print('delete_if_attribute_has_value')

    connection.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
        'ConditionExpression': f'#0 = :value',
        'ExpressionAttributeNames': {
          '#0': attribute
        },
        'ExpressionAttributeValues': {
          ':value': {'N': value}
        }
      }
    })
  
  def version_check(self, connection, id, value):
    connection.write({
      'ConditionCheck': {
        'TableName': self.table_name,
        'Key': {'id': {'S': id}},
        'ConditionExpression': f'#0 = :value',
        'ExpressionAttributeNames': {
          '#0': 'version'
        },
        'ExpressionAttributeValues': {
          ':value': {'N': str(value)}
        }
      }
    })
