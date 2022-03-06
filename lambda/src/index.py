import boto3
import datetime
import json
import string
import random

def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.ap-southeast-2.amazonaws.com")

    table = dynamodb.Table('UncomfortableQuestionsLobbies')


    key = generate_lobby_code(table)

    create_lobby(table, key)

    # response = delete_item(table)

    response = scan_table(table)

    print(response)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }

def generate_lobby_code(table):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    while lobby_exists(table, key):
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    return key


def scan_table(table):
    return table.scan()


def get_lobby(table, key):
    response = table.get_item(
        Key={"LobbyId": key}
    )
    return response

def lobby_exists(table, key):
    return "Item" in get_lobby(table, key)


def delete_lobby(table, key):
    response = table.delete_item(
        Key={"LobbyId": key}
    )
    return response 


def create_lobby(table, key):
    ttl = (int)((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())

    response = table.put_item(
       Item={
            "LobbyId": key,
            "TimeToLive": ttl,
            "Info": {
                "ColumnA": "bleh",
            },
        }
    )
    return response

if __name__ == '__main__':
    lambda_handler(None, None)