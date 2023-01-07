
import boto3
import json
import os
from datetime import datetime, timedelta, timezone


def start_query(event, context):
  print(event)
  today = datetime.now(timezone.utc)
  yesterday = today - timedelta(days=1)
  date_id = yesterday.strftime('%Y-%m-%d')
  print(f'Starting query for {date_id}')

  session = boto3.Session()
  client = session.client('athena')

  named_query = client.get_named_query(
    NamedQueryId=os.environ['QUERY_ID']
  )['NamedQuery']

  execution_id = client.start_query_execution(
    QueryString=named_query['QueryString'],
    QueryExecutionContext={
      'Database': named_query['Database']
    },
    WorkGroup=named_query['WorkGroup'],
    ExecutionParameters=[f'\'{date_id}\''],
  )['QueryExecutionId']

  return {
    'statusCode': 200,
    'body': json.dumps({'executionId': execution_id}),
  }
 
if __name__ == '__main__':
   os.environ['QUERY_ID'] = '645497ad-6dc5-486d-bcba-aa75589c737a'
   start_query(
    {'version': '0', 'id': '0d8d2c02-c9d4-9f56-88a5-28c97def2ad2', 'detail-type': 'Transformation complete', 'source': 'death.dice', 'account': '314077822992', 'time': '2023-01-07T03:04:45Z', 'region': 'ap-southeast-2', 'resources': [], 'detail': {}}
    ,None
  )
