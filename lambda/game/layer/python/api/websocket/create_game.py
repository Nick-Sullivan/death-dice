
import json

from domain_models.commands import CreateGameCommand
from mediator import mediator


def create_game(event, context):
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(CreateGameCommand(session_id))
    return {'statusCode': 200}
