"""All functions in are lambda entry points"""
import boto3
import json
import random

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


def create_game(event, context):

    connection_id = event['requestContext']['connectionId']

    game_id = interactor.create_game(connection_id)

    response_body = json.loads(event['body'])
    response_body['data'] = game_id
    _send_response(event['requestContext'], response_body)

    return {'statusCode': 200}


def join_game(event, context):
    print(event)

    connection_id = event['requestContext']['connectionId']

    body = json.loads(event['body'])

    response_body = body

    try:
        interactor.join_game(connection_id, body['data'])
    except ValueError as e:
        response_body['error'] = str(e)
    
    _send_response(event['requestContext'], response_body)

    return {'statusCode': 200}


def roll_dice(event, context):
    print(event)

    connection_id = event['requestContext']['connectionId']

    nickname = interactor.get_nickname(connection_id)

    roll = random.randint(1, 6)

    response_body = json.loads(event['body'])
    response_body['author'] = nickname
    response_body['roll'] = roll
    _send_response_to_game(event["requestContext"], response_body)

    return {'statusCode': 200}


def send_message(event, context):
    print(event)

    connection_id = event['requestContext']['connectionId']

    nickname = interactor.get_nickname(connection_id)
    
    response_body = json.loads(event['body'])
    response_body['author'] = nickname

    _send_response_to_game(event["requestContext"], response_body)

    return {'statusCode': 200}


def set_nickname(event, context):

    print(event)

    connection_id = event['requestContext']['connectionId']

    body = json.loads(event['body'])

    interactor.set_nickname(connection_id, body['data'])

    _send_response(event['requestContext'], body)

    return {'statusCode': 200}


def _send_response(request_context, response_body):
    print(request_context)
    print(response_body)

    connection_id = request_context['connectionId']

    endpoint_url = f'https://{request_context["domainName"]}/{request_context["stage"]}'

    _post_to_connection(connection_id, endpoint_url, response_body)


def _send_response_to_game(request_context, response_body):
    connection_id = request_context['connectionId']

    endpoint_url = f'https://{request_context["domainName"]}/{request_context["stage"]}'

    game_id = interactor.get_game_id(connection_id)

    connection_ids = interactor.get_connection_ids_in_game(game_id)

    for connection_id in connection_ids:
        _post_to_connection(connection_id, endpoint_url, response_body)


def _post_to_connection(connection_id, endpoint_url, response_body):
    gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)
    gatewayapi.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(response_body)
    )
