"""All functions in are lambda entry points"""
import json
import random

from game_controller import GameController

controller = GameController()


def lambda_handler(func):
    """Decorator, captures AWS lambda input and provides interactors"""

    def inner(event, context):
        print(f'event: {event}')
        player_id = event['requestContext']['connectionId']
        request=json.loads(event['body']) if 'body' in event else {}
        return func(player_id, request)

    return inner


@lambda_handler
def connect(player_id, request):
    """Called by the WebSocketAPI when a new connection is established"""

    controller.create_player(player_id)

    return {'statusCode': 200}


@lambda_handler
def disconnect(player_id, request):
    """Called by the WebSocketAPI when a connection is to be destroyed"""

    controller.delete_player(player_id)

    return {'statusCode': 200}


@lambda_handler
def create_game(player_id, request):
    """Called by the WebSocketAPI when a player wants to create a new game"""

    controller.create_game(player_id)

    return {'statusCode': 200}


@lambda_handler
def join_game(player_id, request):
    """Called by the WebSocketAPI when a player wants to join an existing game"""

    game_id = request['data']

    controller.join_game(player_id, game_id)

    return {'statusCode': 200}


@lambda_handler
def roll_dice(player_id, request):

    # response = request
    # response['author'] = controller.get_nickname(player_id)
    # response['roll'] = random.randint(1, 6)

    # game_id = controller.get_game_id(player_id)
    # player_ids = controller.get_player_ids_in_game(game_id)
    # player_interactor.send_notification(player_ids, response)

    return {'statusCode': 200}


@lambda_handler
def send_message(player_id, request):

    message = request['data']

    game_id = controller.get_game_id(player_id)

    controller.send_chat(player_id, game_id, message)

    return {'statusCode': 200}


@lambda_handler
def set_nickname(player_id, request):

    nickname = request['data']

    controller.set_nickname(player_id, nickname)

    return {'statusCode': 200}
