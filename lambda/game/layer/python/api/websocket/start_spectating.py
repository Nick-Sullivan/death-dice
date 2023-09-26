
import json

from domain_models.commands import StartSpectatingCommand
from mediator import mediator


def start_spectating(event, context):
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(StartSpectatingCommand(session_id))
    return {'statusCode': 200}
