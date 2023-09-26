
import json

from domain_models.commands import JoinGameCommand
from mediator import mediator


def join_game(event, context):
    request = json.loads(event['body'])
    game_id = request['data']['gameId'].upper()
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(JoinGameCommand(session_id, game_id))
    return {'statusCode': 200}
