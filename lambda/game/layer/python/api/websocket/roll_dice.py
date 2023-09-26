
import json

from domain_models.commands import RollDiceCommand
from mediator import mediator


def roll_dice(event, context):
    request = json.loads(event['body'])
    session_id = request['data'].get('sessionId')
    print(f'session_id: {session_id}')
    mediator.send(RollDiceCommand(session_id))
    return {'statusCode': 200}
