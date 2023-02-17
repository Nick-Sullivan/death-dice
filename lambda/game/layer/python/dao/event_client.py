"""Single instance of EventBridge connection, to reduce connection overhead"""
import boto3
import json
import os

client = boto3.client('events', region_name='ap-southeast-2')


def get_client():
  return client


def publish_new_game_event(game_id: str):
  print(f'Publishing new game event for {game_id}')

  project = os.environ['PROJECT']
  
  client.put_events(
    Entries=[{
        'Source': f'{project}.GameCreated',
        'DetailType': 'Game created',
        'Detail': json.dumps({
          'game_id': game_id,
        }),
        'Resources': [],
    }]
  )
