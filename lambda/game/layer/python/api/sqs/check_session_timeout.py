
import json

from domain_models.commands import CheckSessionTimeoutCommand
from mediator import mediator


def check_session_timeout(event, context):
    for record in event['Records']:
        request = json.loads(record['body'])
        print(request)
        detail = request['detail']
        session_id = detail['session_id']
        print(f'session_id: {session_id}')
        mediator.send(CheckSessionTimeoutCommand(session_id))

    return {'statusCode': 200}
