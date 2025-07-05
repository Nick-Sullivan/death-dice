import json

from domain_models.commands import DestroySessionCommand
from mediator import mediator


def destroy_session(event, context):
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(DestroySessionCommand(session_id))
    return {'statusCode': 200}
