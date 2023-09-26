from domain_models.commands import CreateSessionIdCommand, GetSessionIdCommand
from mediator import mediator


def get_session(event, context):
    connection_id = event['requestContext']['connectionId']
    session_id = mediator.send(GetSessionIdCommand(connection_id))
    if not session_id:
        session_id = mediator.send(CreateSessionIdCommand(connection_id))
    print(f'session_id: {session_id}')
    return {'statusCode': 200}
