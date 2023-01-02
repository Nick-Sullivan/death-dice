
import boto3
import json
import os
import time


def get_statistics(event, context):
  print(event)

  session = boto3.Session()
  client = session.client('athena')

  # response = client.list_named_queries(
  #   WorkGroup=os.environ['WORKGROUP']
  # )

  named_query = client.get_named_query(
    NamedQueryId=os.environ['QUERY_GAME_COUNT_ID']
  )['NamedQuery']

  execution_id = client.start_query_execution(
    QueryString=named_query['QueryString'],
    QueryExecutionContext={
      'Database': named_query['Database']
    },
    WorkGroup=named_query['WorkGroup'],
  )['QueryExecutionId']

  # execution = client.get_query_execution(
  #   QueryExecutionId=execution_id
  # )['QueryExecution']

  # TODO, avoid waiting in a lambda
  time.sleep(1)

  result = client.get_query_results(
    QueryExecutionId=execution_id
  )
  print(result)

  assert result['ResultSet']['Rows'][0]['Data'][0]['VarCharValue'] == 'game_count'

  response = {
    'game_count': result['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']
  }

  return {
    'statusCode': 200,
    'body': json.dumps(response)
  }
