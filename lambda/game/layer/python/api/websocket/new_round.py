
import json

from domain_models.commands import NewRoundCommand
from mediator import mediator


def new_round(event, context):
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(NewRoundCommand(session_id))
    return {'statusCode': 200}
