"""All functions in are lambda entry points"""
import boto3
import json
import random

from db_interactor import DatabaseInteractor


interactor = DatabaseInteractor()


def connect(event, context):
    """Called by the WebSocketAPI when a new connection is established"""

    interactor.create_player(event['requestContext']['connectionId'])

    return {'statusCode': 200}


def disconnect(event, context):
    """Called by the WebSocketAPI when a connection is to be destroyed"""

    player_id = interactor.get_player_id(event['requestContext']['connectionId'])

    interactor.delete_player(player_id)

    return {'statusCode': 200}


def create_game(event, context):

    player_id = interactor.get_player_id(event['requestContext']['connectionId'])

    game_id = interactor.create_game(player_id)

    response_body = json.loads(event['body'])
    response_body['data'] = game_id
    _send_response(event['requestContext'], response_body)

    # _send_game_state(game_id, event['requestContext'])

    return {'statusCode': 200}


def join_game(event, context):
    print(event)

    connection_id = event['requestContext']['connectionId']

    player_id = interactor.get_player_id(connection_id)

    body = json.loads(event['body'])
    game_id = body['data']

    response_body = body

    try:
        interactor.join_game(player_id, game_id)
    except ValueError as e:
        response_body['error'] = str(e)
    
    _send_response(event['requestContext'], response_body)

    # _send_game_state(event['requestContext'], game_id)

    return {'statusCode': 200}


def roll_dice(event, context):
    print(event)

    player_id = interactor.get_player_id(event['requestContext']['connectionId'])

    nickname = interactor.get_nickname(player_id)

    roll = random.randint(1, 6)

    response_body = json.loads(event['body'])
    response_body['author'] = nickname
    response_body['roll'] = roll
    _send_notification_to_players(event["requestContext"], response_body)

    return {'statusCode': 200}


def send_message(event, context):
    print(event)

    player_id = interactor.get_player_id(event['requestContext']['connectionId'])

    nickname = interactor.get_nickname(player_id)
    
    response_body = json.loads(event['body'])
    response_body['author'] = nickname

    _send_notification_to_players(event["requestContext"], response_body)

    return {'statusCode': 200}


def set_nickname(event, context):

    print(event)

    player_id = interactor.get_player_id(event['requestContext']['connectionId'])

    body = json.loads(event['body'])

    interactor.set_nickname(player_id, body['data'])

    _send_response(event['requestContext'], body)

    return {'statusCode': 200}


# def _send_game_state(game_id, requestContext):

#     game_state = interactor.get_game_state(game_id)

#     body = {
#         "action": "gameState",
#         "gameId": game_id,
#         **game_state,
#     }
#     _send_notification_to_players(requestContext, body)


def _send_response(request_context, response_body):
    """Sends a response to the websocket that sent the request"""
    print(request_context)
    print(response_body)

    connection_id = request_context['connectionId']

    endpoint_url = f'https://{request_context["domainName"]}/{request_context["stage"]}'

    _post_to_connection(connection_id, endpoint_url, response_body)


def _send_notification_to_players(request_context, response_body):
    """Sends a message to all the players in the game"""

    connection_id = request_context['connectionId']

    endpoint_url = f'https://{request_context["domainName"]}/{request_context["stage"]}'

    player_id = interactor.get_player_id(connection_id)

    game_id = interactor.get_game_id(connection_id)

    player_ids = interactor.get_player_ids_in_game(game_id)

    for player_id in player_ids:
        connection_id = interactor.get_connection_id(player_id)
        _post_to_connection(connection_id, endpoint_url, response_body)


def _post_to_connection(connection_id, endpoint_url, response_body):
    gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)
    gatewayapi.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(response_body)
    )
