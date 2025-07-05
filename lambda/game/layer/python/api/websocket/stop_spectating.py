
import json

from domain_models.commands import StopSpectatingCommand
from mediator import mediator


def stop_spectating(event, context):
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(StopSpectatingCommand(session_id))
    return {'statusCode': 200}
