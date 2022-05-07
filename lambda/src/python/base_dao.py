from enum import Enum


class TableAttribute(Enum):

  def __init__(self, key, type):
    assert type in {'S', 'N', 'BOOL'}
    self.key = key
    self.type = type


class BaseDao:
  
  table_name = None
  attribute = None

  def __init__(self):
      assert isinstance(self.table_name, str)
      assert issubclass(self.attribute, TableAttribute)
      # TODO - assert ID is in TableAttribute

  def delete(self, connection, id):
    assert isinstance(id, str)
    connection.write({
      'Delete': {
        'TableName': self.table_name,
        'Key': {self.attribute.ID.key: {self.attribute.ID.type: id}},
        'ConditionExpression': f'attribute_exists({self.attribute.ID.key})',
      }
    })

  def set_attribute(self, connection, id, attribute, value):
    assert isinstance(attribute, self.attribute)
    connection.write({
      'Update': {
        'TableName': self.table_name,
        'Key': {self.attribute.ID.key: {self.attribute.ID.type: id}},
        'ConditionExpression': f'attribute_exists({self.attribute.ID.key})',
        'UpdateExpression': f'SET {attribute.key} = :value',
        "ExpressionAttributeValues": {':value': {attribute.type: value}},
      }
    })

  def set_attributes(self, connection, id, attribute_dict):
    assert all([isinstance(a, self.attribute) for a in attribute_dict])

    expressions = []
    values = {}
    for i, (attribute, value) in enumerate(attribute_dict.items()):
      expressions.append(f'{attribute.key} = :{i}')
      values[f':{i}'] = {attribute.type: value}

    update_expression = f'SET ' + ', '.join(expressions)

    connection.write({
      'Update': {
        'TableName': self.table_name,
        'Key': {self.attribute.ID.key: {self.attribute.ID.type: id}},
        'ConditionExpression': f'attribute_exists({self.attribute.ID.key})',
        'UpdateExpression': update_expression,
        "ExpressionAttributeValues": values,
      }
    })

  def get_attribute(self, connection, id, attribute):
    assert isinstance(attribute, self.attribute)
    item = self.get(connection, id)
    return item.get(attribute.key)

  def exists(self, connection, id):
    return self.get(connection, id) != None

  def get(self, connection, id):
    item = connection.read({
      'Get': {
        'TableName': self.table_name,
        'Key': {self.attribute.ID.key: {self.attribute.ID.type: id}},
      }
    })
    return self._parse_item(item['Item']) if 'Item' in item else None

  @staticmethod
  def _parse_item(item):
    return {key: next(iter(value.values())) for key, value in item.items()}
