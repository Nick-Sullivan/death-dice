import random
import string
from datetime import datetime, timezone

from domain_models import GameState
from domain_services.interfaces import GameNotFoundException, IGameStore, ITransaction


class GameStore(IGameStore):
    """Creates, updates and destroys entries in the Game table"""

    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def create(self, item: GameState, transaction: ITransaction):
        assert isinstance(item, GameState)

        item.version = 0
        item.modified_at = datetime.now(timezone.utc)

        transaction.write({
            'Put': {
                'TableName': self.table_name,
                'Item': GameState.serialise(item),
                'ConditionExpression': 'attribute_not_exists(id)',
            }
        })

    def get(self, id: str) -> GameState:

        if not self.is_valid_game_id(id):
            raise GameNotFoundException(f'Invalid game {id}')

        item = self.client.get_item(**{
            'TableName': self.table_name,
            'Key': {'id': {'S': id}}
        })

        if 'Item' not in item:
            raise GameNotFoundException(f'Unable to get game {id}')

        return GameState.deserialise(item['Item'])

    def set(self, item: GameState, transaction: ITransaction):
        assert isinstance(item, GameState)
        assert item.id is not None

        item.version += 1
        item.modified_at = datetime.now(timezone.utc)

        transaction.write({
            'Put': {
                'TableName': self.table_name,
                'Item': GameState.serialise(item),
                'ConditionExpression': 'attribute_exists(id) AND version = :v',
                'ExpressionAttributeValues': {':v': {'N': str(item.version-1)}},
            }
        })

    def delete(self, item: GameState, transaction: ITransaction):
        assert isinstance(item, GameState)
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

    def create_unique_game_id(self) -> str:
        items = self.client.scan(**{
            'TableName': self.table_name,
            'ProjectionExpression': 'id',
        })
        existing_ids = {item['id']['S'] for item in items['Items']}

        game_id = None
        while game_id in existing_ids or game_id is None:
            game_id = ''.join(random.choices(string.ascii_uppercase, k=4))

        return game_id

    def is_valid_game_id(self, game_id: str) -> bool:
        return isinstance(game_id, str) and len(game_id) == 4
