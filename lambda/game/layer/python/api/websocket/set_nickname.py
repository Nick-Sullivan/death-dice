
import json

from domain_models.commands import SetNicknameCommand
from mediator import mediator


def set_nickname(event, context):
    connection_id = event['requestContext']['connectionId']
    request = json.loads(event['body'])
    nickname = request['data']['nickname']
    session_id = request['data'].get('sessionId')
    account_id = request['data'].get('accountId')
    print(f'connection_id: {connection_id}')
    print(f'session_id: {session_id}')
    mediator.send(SetNicknameCommand(session_id, account_id, nickname))
    return {'statusCode': 200}
