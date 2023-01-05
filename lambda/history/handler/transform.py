import awswrangler as wr
import boto3
import itertools
import json
import os
import pandas as pd
from boto3.dynamodb.types import TypeDeserializer
from collections import defaultdict
from dateutil import parser
from decimal import Decimal

deserialiser = TypeDeserializer()
session = boto3.Session()
sqs = session.client('sqs')

MESSAGES_PER_BATCH = 10  # max 10
MAX_BATCHES = 200

def transform(event, context):
   """Converts DynamoDB diff streams into files to be stored in s3"""
   print(event)

   messages = get_sqs_messages()

   if not messages:
      print('No messages to read')
      return

   print(f'Transforming {len(messages)} messages')

   tables = defaultdict(list)
   receipts = []
   for sqs_event in messages:
      receipts.append({
         'Id': sqs_event['MessageId'],
         'ReceiptHandle': sqs_event['ReceiptHandle'],
      })

      dynamodb_event = json.loads(sqs_event['Body'])

      transformed = transform_event(dynamodb_event)

      tables[transformed['table']].append(transformed)

   for table_name, events in tables.items():
      upload_to_s3(table_name, events)

   delete_sqs_messages(receipts)

   return {'statusCode': 200}


def get_sqs_messages():
   messages = []
   for _ in range(MAX_BATCHES):

      response = sqs.receive_message(
         QueueUrl=os.environ['QUEUE_URL'],
         MaxNumberOfMessages=10,  # max
      )

      batch = response.get('Messages')

      if batch is None:
         break

      messages.extend(batch)

   return messages


def delete_sqs_messages(receipts):
   for batch in grouper(receipts, MESSAGES_PER_BATCH):
      sqs.delete_message_batch(
         QueueUrl=os.environ['QUEUE_URL'],
         Entries=batch,
      )


def transform_event(event):
   response = {}
   event_type = event['eventName']

   if event_type in {'INSERT', 'MODIFY'}:
      key_values = event['dynamodb']['NewImage']

   elif event_type == 'REMOVE':
      key_values = event['dynamodb']['OldImage']

   else:
      raise NotImplementedError(event_type)

   response['meta_event_type'] = event_type
   for key, value in key_values.items():
      response[key] = deserialiser.deserialize(value)

   response = remove_decimals(response)

   return response


def remove_decimals(key_values):
   for key, value in key_values.items():
      if isinstance(value, Decimal):
         key_values[key] = int(value)

      elif isinstance(value, dict):
         key_values[key] = remove_decimals(value)
      
      elif isinstance(value, list):
         key_values[key] = [remove_decimals(v) for v in value]

   return key_values


def upload_to_s3(table_name, events):
   print(events)
   bucket_name = os.environ['BUCKET_NAME']

   first_modified_at = min([e['modified_at'] for e in events])

   date = parser.parse(first_modified_at)
   year = date.strftime('%Y')
   month = date.strftime('%m')
   day = date.strftime('%d')
   file = first_modified_at
   key = f's3://{bucket_name}/data/table={table_name}/year={year}/month={month}/day={day}/{file}.parquet'

   df = pd.DataFrame(events)
   wr.s3.to_parquet(
      df=df,
      path=key,
   )


def grouper(iterable, n):
    "Batch data into iterators of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield list(itertools.chain((first_el,), chunk_it))


if __name__ == '__main__':
   os.environ['BUCKET_NAME'] = 'fake-bucket'
   os.environ['QUEUE_URL'] = 'https://sqs.ap-southeast-2.amazonaws.com/314077822992/DeathDiceStage-Extract'
   transform(
      {'version': '0', 'id': 'bdab8054-fda8-3d4f-41df-eeaa317a95c5', 'detail-type': 'Scheduled Event', 'source': 'aws.events', 'account': '314077822992', 'time': '2023-01-05T07:57:14Z', 'region': 'ap-southeast-2', 'resources': ['arn:aws:events:ap-southeast-2:314077822992:rule/DeathDiceStage-Transform'], 'detail': {}}
      , None)
