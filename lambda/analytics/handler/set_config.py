
import json
import os

import boto3
from boto3.dynamodb.types import TypeDeserializer

deserialiser = TypeDeserializer()

session = boto3.Session()
dynamodb = session.client('dynamodb')

def set_config(event, context):
  print(event)

  body = event.get('body')
  if body is None:
    return {
      'statusCode': 400,
      'body': json.dumps({'error': 'body is required'})
    }

  body = json.loads(body)
  for key, value in body.items():
    print(f'Setting {key} to {value}')
    if isinstance(value, str):
        value = value.lower() == 'true'

    dynamodb.put_item(
      TableName=os.environ['RESULT_CONFIG_TABLE_NAME'],
      Item={
        'config_key': {'S': key},
        'value': {'BOOL': value},
      }
    )

  return {
    'statusCode': 200,
  }


if __name__ == '__main__':
  os.environ['RESULT_CONFIG_TABLE_NAME'] = "DeathDiceStageAnalyticsConfig"
  set_config(
    {'resource': '/statistics', 'path': '/statistics', 'httpMethod': 'POST', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '4764', 'CloudFront-Viewer-Country': 'AU', 'Content-Type': 'application/json', 'Host': 'ywl3csgtaf.execute-api.ap-southeast-2.amazonaws.com', 'Postman-Token': 'bc5bed8c-8df1-4dc7-ad8c-599fe51a1c2c', 'User-Agent': 'PostmanRuntime/7.30.0', 'Via': '1.1 50cd7efdc991cdb2495efa15524688d6.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'qw1ajbGQz3OAbU0PaVjItx6Wxml-zWIGBksokFteM9QGmG_N0oriFg==', 'X-Amzn-Trace-Id': 'Root=1-63b526d9-01448222720628fd1548544a', 'X-Forwarded-For': '180.150.112.211, 130.176.108.112', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['4764'], 'CloudFront-Viewer-Country': ['AU'], 'Content-Type': ['application/json'], 'Host': ['ywl3csgtaf.execute-api.ap-southeast-2.amazonaws.com'], 'Postman-Token': ['bc5bed8c-8df1-4dc7-ad8c-599fe51a1c2c'], 'User-Agent': ['PostmanRuntime/7.30.0'], 'Via': ['1.1 50cd7efdc991cdb2495efa15524688d6.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['qw1ajbGQz3OAbU0PaVjItx6Wxml-zWIGBksokFteM9QGmG_N0oriFg=='], 'X-Amzn-Trace-Id': ['Root=1-63b526d9-01448222720628fd1548544a'], 'X-Forwarded-For': ['180.150.112.211, 130.176.108.112'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'gr67yp', 'resourcePath': '/statistics', 'httpMethod': 'POST', 'extendedRequestId': 'eNMB8H81ywMFkYA=', 'requestTime': '04/Jan/2023:07:12:25 +0000', 'path': '/v1/statistics', 'accountId': '314077822992', 'protocol': 'HTTP/1.1', 'stage': 'v1', 'domainPrefix': 'ywl3csgtaf', 'requestTimeEpoch': 1672816345021, 'requestId': 'a793bbc9-3444-405b-b44c-1a05e46d43ed', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '180.150.112.211', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.30.0', 'user': None}, 'domainName': 'ywl3csgtaf.execute-api.ap-southeast-2.amazonaws.com', 'apiId': 'ywl3csgtaf'}, 'body': '{\r\n    "account_id": "a0f58cca-671d-49e9-b54e-7473099cfef8"\r\n}', 'isBase64Encoded': False}  # noqa: E501
    ,None
  )