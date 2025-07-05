import awswrangler as wr
import boto3
import json
import os
import pandas as pd

from sqs_interactor import SqsInteractor
from transformer import MessageTransformer


session = boto3.Session()
sqs = SqsInteractor(session.client('sqs'))
transformer = MessageTransformer()
event_bridge = session.client('events')


def transform(event, context):
   """Converts DynamoDB diff streams into files to be stored in s3"""
   print(event)

   messages = sqs.get_messages()

   if not messages:
      print('No messages to read')
      return

   print(f'Transforming {len(messages)} messages')

   transformer.load_messages(messages)
   message_groups = transformer.get_transformed_messages()
   date_ids = transformer.get_unique_date_ids()

   for message in message_groups:
      upload_to_s3(message.table_name, message.date_id, message.events)

   sqs.delete_messages()

   publish_event(date_ids)

   return {'statusCode': 200}


def upload_to_s3(table_name, date_id, events):
   bucket_name = os.environ['BUCKET_NAME']
   first_modified_at = min([e['modified_at'] for e in events])
   key = f's3://{bucket_name}/data/table={table_name}/date_id={date_id}/{first_modified_at}.parquet'

   wr.s3.to_parquet(
      df=pd.DataFrame(events),
      path=key,
   )


def publish_event(date_ids):
   event_bridge.put_events(
      Entries=[{
         'Source': os.environ['EVENT_SOURCE'],
         'DetailType': 'Transformation complete',
         'Detail': json.dumps({
            'date_ids': sorted(date_ids),
         }),
         'Resources': [],
      }]
   )


if __name__ == '__main__':
   os.environ['BUCKET_NAME'] = 'fake-bucket'
   os.environ['QUEUE_URL'] = 'https://sqs.ap-southeast-2.amazonaws.com/314077822992/DeathDiceStage-Extract'
   transform(
      {'version': '0', 'id': 'bdab8054-fda8-3d4f-41df-eeaa317a95c5', 'detail-type': 'Scheduled Event', 'source': 'aws.events', 'account': '314077822992', 'time': '2023-01-05T07:57:14Z', 'region': 'ap-southeast-2', 'resources': ['arn:aws:events:ap-southeast-2:314077822992:rule/DeathDiceStage-Transform'], 'detail': {}}  # noqa: E501
      , None)
