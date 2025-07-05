
import boto3
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

session = boto3.Session()
athena = session.client('athena')
dynamodb = session.client('dynamodb')


def cache_result(event, context):
  print(event)

  result = athena.get_query_results(QueryExecutionId=event['detail']['queryExecutionId'])
  
  rows = parse_athena_result(result, default='0')

  grouped = group_results(rows)

  for group in grouped:
    dynamodb.put_item(
      TableName=os.environ['RESULT_CACHE_TABLE_NAME'],
      Item={
        'account_id': {'S': group['account_id']},
        'date_id': {'S': group['date_id']},
        'value': {'S': json.dumps(group)},
        'modified_at': {'S': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')},
      }
    )


def parse_athena_result(athena_result, default=None):
  header_raw, *rows_raw = athena_result['ResultSet']['Rows']
  header = get_var_char_values(header_raw, default)
  return [dict(zip(header, get_var_char_values(row, default))) for row in rows_raw]


def get_var_char_values(d, default):
  return [obj.get('VarCharValue', default) for obj in d['Data']]


def group_results(rows):
  result_dict = defaultdict(dict)
  for row in rows:
    name = row['metric']
    value = row['count']
    key = (row['account_id'], row['date_id'])
    result_dict[key][name] = value

  result_list = []
  for (account_id, date_id), metrics in result_dict.items():
    metrics['account_id'] = account_id
    metrics['date_id'] = date_id
    result_list.append(metrics)

  return result_list


if __name__ == '__main__':
  os.environ['RESULT_CACHE_TABLE_NAME'] = "DeathDiceStageAnalytics"
  cache_result(
    {'version': '0', 'id': 'ccceb78e-85ac-7155-c4e6-e628f55caa9b', 'detail-type': 'Athena Query State Change', 'source': 'aws.athena', 'account': '314077822992', 'time': '2023-01-06T23:41:19Z', 'region': 'ap-southeast-2', 'resources': [], 'detail': {'currentState': 'SUCCEEDED', 'previousState': 'RUNNING', 'queryExecutionId': '5a348467-bba0-44be-8e2d-9c877107b7ad', 'sequenceNumber': '3', 'statementType': 'DML', 'versionId': '0', 'workgroupName': 'DeathDiceStageAnalytics'}}  # noqa: E501
    ,None
  )
