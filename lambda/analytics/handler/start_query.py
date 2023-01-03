
import boto3
import json
import os


def start_query(event, context):
  print(event)

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
  )['QueryExecutionId']

  return {
    'statusCode': 200,
    'body': json.dumps({'executionId': execution_id}),
  }
 
if __name__ == '__main__':
   os.environ['QUERY_ID'] = 'e9a422c6-2db5-45db-b861-0be5949679c6'
   start_query(
    {'resource': '/statistics', 'path': '/statistics', 'httpMethod': 'POST', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '4764', 'CloudFront-Viewer-Country': 'AU', 'Content-Type': 'application/json', 'Host': 'oulnjyzov4.execute-api.ap-southeast-2.amazonaws.com', 'Postman-Token': '862c58ba-196f-41fa-99c0-321d5a279ade', 'User-Agent': 'PostmanRuntime/7.30.0', 'Via': '1.1 7563cdb400fdf01a6013c0143ee53c58.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'Y2xNgihxUlFe73DpbZcUicm7aVCLmzYwy0yVN3XjV0789QPCCLjSSg==', 'X-Amzn-Trace-Id': 'Root=1-63b26df3-3994178e7f8633920e39255f', 'X-Forwarded-For': '180.150.112.211, 130.176.108.113', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['4764'], 'CloudFront-Viewer-Country': ['AU'], 'Content-Type': ['application/json'], 'Host': ['oulnjyzov4.execute-api.ap-southeast-2.amazonaws.com'], 'Postman-Token': ['862c58ba-196f-41fa-99c0-321d5a279ade'], 'User-Agent': ['PostmanRuntime/7.30.0'], 'Via': ['1.1 7563cdb400fdf01a6013c0143ee53c58.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['Y2xNgihxUlFe73DpbZcUicm7aVCLmzYwy0yVN3XjV0789QPCCLjSSg=='], 'X-Amzn-Trace-Id': ['Root=1-63b26df3-3994178e7f8633920e39255f'], 'X-Forwarded-For': ['180.150.112.211, 130.176.108.113'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'obn311', 'resourcePath': '/statistics', 'httpMethod': 'POST', 'extendedRequestId': 'eGYeIHrpSwMFybw=', 'requestTime': '02/Jan/2023:05:38:59 +0000', 'path': '/v1/statistics', 'accountId': '314077822992', 'protocol': 'HTTP/1.1', 'stage': 'v1', 'domainPrefix': 'oulnjyzov4', 'requestTimeEpoch': 1672637939800, 'requestId': '65d00022-a3ea-4410-919a-29405159c50b', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '180.150.112.211', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.30.0', 'user': None}, 'domainName': 'oulnjyzov4.execute-api.ap-southeast-2.amazonaws.com', 'apiId': 'oulnjyzov4'}, 'body': '{\r\n    "account_id": "66983d86-b78d-4984-a408-d17c22af6610"\r\n}', 'isBase64Encoded': False}
    ,None
  )
