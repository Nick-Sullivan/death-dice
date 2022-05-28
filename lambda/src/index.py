"""All functions in are lambda entry points"""
import json

from game_controller import GameController

controller = GameController()


def lambda_handler(func):
    """Decorator, parses AWS lambda input"""

    def inner(event, context):
        connection_id = event['requestContext']['connectionId']
        request=json.loads(event['body']) if 'body' in event else {}
        return func(connection_id, request)

    return inner


@lambda_handler
def connect(connection_id, request):
    """Called by the WebSocketAPI when a new connection is established"""

    controller.connect(connection_id)

    return {'statusCode': 200}


@lambda_handler
def disconnect(connection_id, request):
    """Called by the WebSocketAPI when a connection is to be destroyed"""

    controller.disconnect(connection_id)

    return {'statusCode': 200}


@lambda_handler
def create_game(connection_id, request):
    """Called by the WebSocketAPI when a player wants to create a new game"""

    controller.create_game(connection_id)

    return {'statusCode': 200}


@lambda_handler
def join_game(connection_id, request):
    """Called by the WebSocketAPI when a player wants to join an existing game"""

    game_id = request['data'].upper()

    controller.join_game(connection_id, game_id)

    return {'statusCode': 200}


@lambda_handler
def new_round(connection_id, request):
    """Called by the WebSocketAPI when a player wants to start the next round"""

    controller.new_round(connection_id)

    return {'statusCode': 200}


@lambda_handler
def roll_dice(connection_id, request):
    """Called by the WebSocketAPI when a player wants to roll dice in the current round"""

    controller.roll_dice(connection_id)

    return {'statusCode': 200}


@lambda_handler
def set_nickname(connection_id, request):
    """Called by the WebSocketAPI when a player wants set their display name"""

    nickname = request['data']

    controller.set_nickname(connection_id, nickname)

    return {'statusCode': 200}
