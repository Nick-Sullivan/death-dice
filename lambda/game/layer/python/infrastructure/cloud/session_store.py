from datetime import datetime, timezone

from domain_models import SessionItem
from domain_services.interfaces import ISessionStore, ITransaction, SessionNotFoundException


class SessionStore(ISessionStore):
    """Creates, updates and destroys entries in the Connection table"""

    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def create(self, item: SessionItem, transaction: ITransaction):
        assert isinstance(item, SessionItem)

        item.version = 0
        item.modified_at = datetime.now(timezone.utc)

        transaction.write({
            'Put': {
                'TableName': self.table_name,
                'Item': SessionItem.serialise(item),
                'ConditionExpression': 'attribute_not_exists(id)',
            }
        })

    def get(self, id: str) -> SessionItem:
        assert isinstance(id, str)

        item = self.client.get_item(**{
            'TableName': self.table_name,
            'Key': {'id': {'S': id}},
        })

        if 'Item' not in item:
            raise SessionNotFoundException(f'Unable to get connection {id}')

        return SessionItem.deserialise(item['Item'])

    def set(self, item: SessionItem, transaction: ITransaction):
        assert isinstance(item, SessionItem)
        assert item.id is not None

        item.version += 1
        item.modified_at = datetime.now(timezone.utc)

        transaction.write({
            'Put': {
                'TableName': self.table_name,
                'Item': SessionItem.serialise(item),
                'ConditionExpression': 'attribute_exists(id) AND version = :v',
                'ExpressionAttributeValues': {':v': {'N': str(item.version-1)}},
            }
        })

    def delete(self, item: SessionItem, transaction: ITransaction):
        assert isinstance(item, SessionItem)
        transaction.write({
            'Delete': {
                'TableName': self.table_name,
                'Key': {'id': {'S': item.id}},
                'ConditionExpression': 'attribute_exists(id) AND version = :v',
                'ExpressionAttributeValues': {
                    ':v': {'N': str(item.version)},
                },
            }
        })
