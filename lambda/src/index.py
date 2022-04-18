"""All functions in are lambda entry points"""

import boto3
import json

from lobby_interactor import LobbyInteractor


interactor = LobbyInteractor('UncomfortableQuestionsLobbies')


def connect(event, context):
    """Called by the WebSocketAPI when a new connection is established"""

    connection_id = event['requestContext']['connectionId']

    interactor.create(connection_id)

    return {'statusCode': 200}


def disconnect(event, context):
    """Called by the WebSocketAPI when a connection is to be destroyed"""

    connection_id = event['requestContext']['connectionId']

    interactor.delete(connection_id)

    return {'statusCode': 200}


def join_lobby(event, context):

    connection_id = event['requestContext']['connectionId']

    interactor.join_lobby(connection_id, "lobbynew")

    return {'statusCode': 200}


def send_message(event, context):

    print(event)

    connection_id = event['requestContext']['connectionId']

    message = json.loads(event['body'])['message']

    endpoint_url = f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}'

    lobby_id = interactor.get_lobby_id(connection_id)
    print(f'lobby_id: {lobby_id}')

    connection_ids = interactor.get_connection_ids_in_lobby(lobby_id)
    print(f'connection_ids: {connection_ids}')

    gatewayapi = boto3.client(
      "apigatewaymanagementapi",
      endpoint_url = endpoint_url
    )
    
    for connection_id in connection_ids:
        gatewayapi.post_to_connection(
            ConnectionId=connection_id,
            Data=message
        )

    return {'statusCode': 200}
