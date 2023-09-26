from domain_models.commands import DestroyConnectionCommand
from mediator import mediator


def disconnect(event, context):
    connection_id = event['requestContext']['connectionId']
    print(f'connection_id: {connection_id}')
    mediator.send(DestroyConnectionCommand(connection_id))
    return {'statusCode': 200}

