
import boto3
import json
import os
from datetime import datetime, timezone

def cache_result(event, context):
  print(event)

  session = boto3.Session()

  athena = session.client('athena')
  result = athena.get_query_results(QueryExecutionId=event['detail']['queryExecutionId'])
  rows = parse_athena_result(result, default='0')
  print(rows)

  id = rows[0]['date_id']

  dynamodb = session.client('dynamodb')
  dynamodb.put_item(
    TableName=os.environ['RESULT_CACHE_TABLE_NAME'],
    Item={
      'id': {'S': id},
      'value': {'S': json.dumps(rows)},
      'modified_at': {'S': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')},
    }
  )


def parse_athena_result(athena_result, default=None):
  header_raw, *rows_raw = athena_result['ResultSet']['Rows']
  header = get_var_char_values(header_raw, default)
  return [dict(zip(header, get_var_char_values(row, default))) for row in rows_raw]


def get_var_char_values(d, default):
  return [obj.get('VarCharValue', default) for obj in d['Data']]


if __name__ == '__main__':
  os.environ['RESULT_CACHE_TABLE_NAME'] = "DeathDiceStageAnalytics"
  cache_result(
    {'version': '0', 'id': '920a15c3-1b71-693e-fce9-a64e63fa56cf', 'detail-type': 'Athena Query State Change', 'source': 'aws.athena', 'account': '314077822992', 'time': '2023-01-03T08:33:21Z', 'region': 'ap-southeast-2', 'resources': [], 'detail': {'currentState': 'SUCCEEDED', 'previousState': 'RUNNING', 'queryExecutionId': 'bba15bf0-0427-4c1d-aace-66ef5b895aa7', 'sequenceNumber': '3', 'statementType': 'DML', 'versionId': '0', 'workgroupName': 'DeathDiceStage'}}
    ,None
  )
