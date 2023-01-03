# Uploads DynamoDB stream events to S3

import boto3
import json
import os
import awswrangler as wr
import pandas as pd
from boto3.dynamodb.types import TypeDeserializer
from collections import defaultdict
from dateutil import parser
from decimal import Decimal

deserialiser = TypeDeserializer()


def transform(event, context):
   """Converts DynamoDB diff streams into files to be stored in s3"""
   print(event)
   print(f"Processing {len(event['Records'])} records")

   tables = defaultdict(list)
   for event in event['Records']:
      transformed = transform_event(event)
      tables[transformed['table']].append(transformed)

   for table_name, events in tables.items():
      upload_to_s3(table_name, events)

   return {'statusCode': 200}


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

   # json_key =  f'data/table={table_name}Json/year={year}/month={month}/{file}.json'
   # s3 = boto3.client('s3')
   # s3.put_object(
   #    Bucket=bucket_name,
   #    Key=json_key,
   #    Body="\r\n".join([json.dumps(e) for e in events])  # format required for Athena to process
   # )


if __name__ == '__main__':
   os.environ['BUCKET_NAME'] = 'fake-bucket'
   transform({
   "Records":[
      {
         "eventID":"acd0f19d36dbca5a133b6104c0534b02",
         "eventName":"INSERT",
         "eventVersion":"1.1",
         "eventSource":"aws:dynamodb",
         "awsRegion":"ap-southeast-2",
         "dynamodb":{
            "ApproximateCreationDateTime":1672611741.0,
            "Keys":{
               "id":{
                  "S":"eFYghdMoywMCIZA="
               }
            },
            "NewImage":{
               "account_id":{
                  "NULL":"true"
               },
               "nickname":{
                  "NULL":"true"
               },
               "modified_action":{
                  "S":"CREATE_CONNECTION"
               },
               "id":{
                  "S":"eFYghdMoywMCIZA="
               },
               "modified_at":{
                  "S":"2023-01-01 22:22:21.281469"
               },
               "version":{
                  "N":"0"
               },
               "table":{
                  "S":"Connection"
               },
               "game_id":{
                  "NULL":"true"
               }
            },
            "SequenceNumber":"1800000000013882780252",
            "SizeBytes":156,
            "StreamViewType":"NEW_AND_OLD_IMAGES"
         },
         "eventSourceARN":"arn:aws:dynamodb:ap-southeast-2:314077822992:table/DeathDiceStage/stream/2023-01-01T21:13:29.879"
      },
      {
         "eventID":"00334d4db01316d819dceec3927ce93d",
         "eventName":"REMOVE",
         "eventVersion":"1.1",
         "eventSource":"aws:dynamodb",
         "awsRegion":"ap-southeast-2",
         "dynamodb":{
            "ApproximateCreationDateTime":1672611743.0,
            "Keys":{
               "id":{
                  "S":"eFYghdMoywMCIZA="
               }
            },
            "OldImage":{
               "account_id":{
                  "NULL":"true"
               },
               "nickname":{
                  "NULL":"true"
               },
               "modified_action":{
                  "S":"CREATE_CONNECTION"
               },
               "id":{
                  "S":"eFYghdMoywMCIZA="
               },
               "modified_at":{
                  "S":"2023-01-01 22:22:21.281469"
               },
               "version":{
                  "N":"0"
               },
               "table":{
                  "S":"Connection"
               },
               "game_id":{
                  "NULL":"true"
               }
            },
            "SequenceNumber":"1900000000013882780892",
            "SizeBytes":156,
            "StreamViewType":"NEW_AND_OLD_IMAGES"
         },
         "eventSourceARN":"arn:aws:dynamodb:ap-southeast-2:314077822992:table/DeathDiceStage/stream/2023-01-01T21:13:29.879"
      }
   ]
}
   , None)
