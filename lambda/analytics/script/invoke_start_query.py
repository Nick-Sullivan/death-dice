import boto3
import json


if __name__ == '__main__':
   session = boto3.Session()
   client = session.client('lambda')

   client.invoke(
      FunctionName='DeathDiceStageAnalytics-StartQuery',
      Payload=json.dumps({
         'version': '0',
         'id': 'bb960e56-72ef-d31f-9d56-19d2cfb5de9b',
         'detail-type': 'Transformation complete',
         'source': 'DeathDiceStage.Transform',
         'account': '314077822992',
         'time': '2023-01-09T06:00:35Z',
         'region': 'ap-southeast-2',
         'resources': [],
         'detail': {'date_ids': ['2023-01-09']}
      })
   )
   