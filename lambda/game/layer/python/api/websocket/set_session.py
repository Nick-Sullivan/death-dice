
import json

from domain_models.commands import SetSessionIdCommand
from mediator import mediator


def set_session(event, context):
    connection_id = event['requestContext']['connectionId']
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(SetSessionIdCommand(connection_id, session_id))
    return {'statusCode': 200}
