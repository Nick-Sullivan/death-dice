import boto3
import json


def get_s3_objects(session):
   s3_client = session.client('s3')
   return s3_client.list_objects_v2(
      Bucket='death-dice-database-history',
      Prefix='data/table=Game'
   )

def get_date_id_from_name(file_name):
   return file_name.split('/')[2][8:]


if __name__ == '__main__':
   session = boto3.Session()

   s3_objects = get_s3_objects(session)
   date_ids = sorted({get_date_id_from_name(f['Key']) for f in s3_objects['Contents']})

   # date_ids = ['2023-01-09']

   lambda_client = session.client('lambda')
   lambda_client.invoke(
      FunctionName='DeathDiceAnalytics-StartQuery',
      Payload=json.dumps({
         'version': '0',
         'id': 'bb960e56-72ef-d31f-9d56-19d2cfb5de9b',
         'detail-type': 'Transformation complete',
         'source': 'DeathDiceStage.Transform',
         'account': '314077822992',
         'time': '2023-01-09T06:00:35Z',
         'region': 'ap-southeast-2',
         'resources': [],
         'detail': {'date_ids': date_ids}
      })
   )
   