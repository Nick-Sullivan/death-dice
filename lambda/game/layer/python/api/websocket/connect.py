
from domain_models.commands import CreateConnectionCommand
from mediator import mediator


def connect(event, context):
    connection_id = event['requestContext']['connectionId']
    print(f'connection_id: {connection_id}')
    mediator.send(CreateConnectionCommand(connection_id))
    return {'statusCode': 200}
