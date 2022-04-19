"""All functions in are lambda entry points"""

import boto3
import json

from db_interactor import DatabaseInteractor


interactor = DatabaseInteractor()


def connect(event, context):
    """Called by the WebSocketAPI when a new connection is established"""

    connection_id = event['requestContext']['connectionId']

    interactor.create_connection(connection_id)

    return {'statusCode': 200}


def disconnect(event, context):
    """Called by the WebSocketAPI when a connection is to be destroyed"""

    connection_id = event['requestContext']['connectionId']

    interactor.delete_connection(connection_id)

    return {'statusCode': 200}


def join_game(event, context):

    connection_id = event['requestContext']['connectionId']

    game_id = json.loads(event['body'])['data']

    interactor.create_game(connection_id)
    # interactor.join_game(connection_id, game_id)

    _send_response(event)

    return {'statusCode': 200}


def send_message(event, context):

    print(event)

    connection_id = event['requestContext']['connectionId']

    game_id = interactor.get_game_id(connection_id)
    print(f'game_id: {game_id}')

    connection_ids = interactor.get_connection_ids_in_game(game_id)
    print(f'connection_ids: {connection_ids}')

    endpoint_url = f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}'
    gatewayapi = boto3.client(
      "apigatewaymanagementapi",
      endpoint_url = endpoint_url
    )
    
    # message = json.loads(event['body'])['data']

    for connection_id in connection_ids:
        gatewayapi.post_to_connection(
            ConnectionId=connection_id,
            Data=event['body']
        )

    return {'statusCode': 200}


def set_nickname(event, context):

    print(event)

    connection_id = event['requestContext']['connectionId']

    nickname = json.loads(event['body'])['data']

    interactor.set_nickname(connection_id, nickname)

    _send_response(event)

    return {'statusCode': 200}


def _send_response(event):
    connection_id = event['requestContext']['connectionId']

    endpoint_url = f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}'

    gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)
    gatewayapi.post_to_connection(
        ConnectionId=connection_id,
        Data=event['body']
    )
