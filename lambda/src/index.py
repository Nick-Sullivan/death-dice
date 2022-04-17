"""All functions in are lambda entry points"""

import boto3
import json

from lobby_interactor import LobbyInteractor


interactor = LobbyInteractor('UncomfortableQuestionsLobbies')


def connect(event, context):
    """Called by the WebSocketAPI when a new connection is established"""

    id = event['requestContext']['connectionId']

    interactor.create(id)

    return {'statusCode': 200}


def disconnect(event, context):
    """Called by the WebSocketAPI when a connection is to be destroyed"""

    id = event['requestContext']['connectionId']

    interactor.delete(id)

    return {'statusCode': 200}


def send_message(event, context):

    print(event)

    id = event['requestContext']['connectionId']

    data = json.loads(event['body'])['message']

    endpoint_url = f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}'

    gatewayapi = boto3.client(
      "apigatewaymanagementapi",
      endpoint_url = endpoint_url
    )
    gatewayapi.post_to_connection(
        ConnectionId=id,
        Data=data
    )

    return {'statusCode': 200}
