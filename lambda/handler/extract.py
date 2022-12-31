# Called by Kinesis 
# https://docs.aws.amazon.com/kinesisanalytics/latest/dev/lambda-preprocessing.html

import base64
import json
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

deserialiser = TypeDeserializer()


def extract(event, context):
  """When DynamoDB is updated, stores the values in s3"""
  print(event)

  output = []
  for record in event['records']:
    event = decode(record['data'])
    transformed = transform_event(event)
    encoded = encode(transformed)

    output.append({
      'recordId': record['recordId'],
      'result': 'Ok',
      'data': encoded,
      'metadata': {
        'partitionKeys': {
          'table': transformed['table']
        }
      }
    })

  return {'records': output}


def decode(data_b64):
  data_bstr = base64.b64decode(data_b64)
  data_json = json.loads(data_bstr)
  return data_json


def encode(data_json):
  data_str = json.dumps(data_json)
  data_bstr = data_str.encode("utf-8")
  data_b64 = base64.b64encode(data_bstr).decode("utf-8")
  return data_b64


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

  print(response)
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


if __name__ == '__main__':
  extract({
   "invocationId":"15acd46a-6de3-49d7-a506-974b273ef4ae",
   "sourceKinesisStreamArn":"arn:aws:kinesis:ap-southeast-2:314077822992:stream/DeathDiceStage",
   "deliveryStreamArn":"arn:aws:firehose:ap-southeast-2:314077822992:deliverystream/DeathDiceStage",
   "region":"ap-southeast-2",
   "records":[
      {
         "recordId":"49636604002855157398639321286259680911899983401516531714000000",
         "approximateArrivalTimestamp":1672443354228,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiIzOTljYzU1Zi1mZmQ3LTRmY2EtOTQwZS1kZTIzMzUyYzI0ZDciLCJldmVudE5hbWUiOiJJTlNFUlQiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM1MzkzMywiS2V5cyI6eyJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMCJ9LCJuaWNrbmFtZSI6eyJOVUxMIjp0cnVlfSwibGFzdF9hY3Rpb24iOnsiUyI6IkNSRUFURV9DT05ORUNUSU9OIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzU6NTMuNjYwMTQyKzAwOjAwIn0sImdhbWVfaWQiOnsiTlVMTCI6dHJ1ZX19LCJTaXplQnl0ZXMiOjE0Mn0sImV2ZW50U291cmNlIjoiYXdzOmR5bmFtb2RiIn0=",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286259680911899983401516531714",
            "subsequenceNumber":0,
            "partitionKey":"3077CF05FAE4106AE15DE489A4BEDD9E",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443354228
         }
      },
      {
         "recordId":"49636604002855157398639321286260889837719598649166528514000000",
         "approximateArrivalTimestamp":1672443363261,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiIzZjdhZDFkYS0wZTc4LTQxMjQtYjljZC04NmFhZTA5MmJjYjAiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM2MzAxNCwiS2V5cyI6eyJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMSJ9LCJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiU0VUX05JQ0tOQU1FIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzU6NTMuNjYwMTQyKzAwOjAwIn0sImdhbWVfaWQiOnsiTlVMTCI6dHJ1ZX19LCJPbGRJbWFnZSI6eyJ2ZXJzaW9uIjp7Ik4iOiIwIn0sIm5pY2tuYW1lIjp7Ik5VTEwiOnRydWV9LCJsYXN0X2FjdGlvbiI6eyJTIjoiQ1JFQVRFX0NPTk5FQ1RJT04ifSwiYWNjb3VudF9pZCI6eyJOVUxMIjp0cnVlfSwiaWQiOnsiUyI6ImQtOVo5ZnBweXdNQ0lsdz0ifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMi0xMi0zMCAyMzozNTo1My42NjAxNDIrMDA6MDAifSwiZ2FtZV9pZCI6eyJOVUxMIjp0cnVlfX0sIlNpemVCeXRlcyI6MjY1fSwiZXZlbnRTb3VyY2UiOiJhd3M6ZHluYW1vZGIifQ==",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286260889837719598649166528514",
            "subsequenceNumber":0,
            "partitionKey":"3077CF05FAE4106AE15DE489A4BEDD9E",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443363261
         }
      },
      {
         "recordId":"49636604002855157398639321286262098763539213621938618370000000",
         "approximateArrivalTimestamp":1672443368275,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJkMjk0MDcxZC02Y2RmLTRjMjAtOWEwMi04MmExMDY4NTkwMDEiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM2ODAxMSwiS2V5cyI6eyJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiU0VUX05JQ0tOQU1FIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImdhbWVfaWQiOnsiUyI6IkNQRlIifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMi0xMi0zMCAyMzozNTo1My42NjAxNDIrMDA6MDAifX0sIk9sZEltYWdlIjp7InZlcnNpb24iOnsiTiI6IjEifSwibmlja25hbWUiOnsiUyI6Ik5pY2sifSwibGFzdF9hY3Rpb24iOnsiUyI6IlNFVF9OSUNLTkFNRSJ9LCJhY2NvdW50X2lkIjp7Ik5VTEwiOnRydWV9LCJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJnYW1lX2lkIjp7Ik5VTEwiOnRydWV9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIyLTEyLTMwIDIzOjM1OjUzLjY2MDE0MiswMDowMCJ9fSwiU2l6ZUJ5dGVzIjoyNjd9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286262098763539213621938618370",
            "subsequenceNumber":0,
            "partitionKey":"3077CF05FAE4106AE15DE489A4BEDD9E",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443368275
         }
      },
      {
         "recordId":"49636604002855157398639321286263307689358828319832801282000000",
         "approximateArrivalTimestamp":1672443368879,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiI0N2ZhZjlmMi1lM2YzLTRmMDQtOWU5OS04MmI5NzFjZGJhNzUiLCJldmVudE5hbWUiOiJJTlNFUlQiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM2ODAxMSwiS2V5cyI6eyJpZCI6eyJTIjoiQ1BGUiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMCJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJ3aW5fY291bnRlciI6eyJOIjoiMCJ9LCJyb2xscyI6eyJMIjpbXX0sIm91dGNvbWUiOnsiUyI6IiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sIm1yX2VsZXZlbiI6eyJTIjoiIn0sImxhc3RfYWN0aW9uIjp7IlMiOiJDUkVBVEVfR0FNRSJ9LCJsYXN0X2FjdGlvbl9ieSI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJpZCI6eyJTIjoiQ1BGUiJ9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIyLTEyLTMwIDIzOjM2OjA3LjkzNTg2NCswMDowMCJ9fSwiU2l6ZUJ5dGVzIjoyMjR9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286263307689358828319832801282",
            "subsequenceNumber":0,
            "partitionKey":"514F6C95D3B4A0F12008B5B9563BFE6D",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443368879
         }
      },
      {
         "recordId":"49636604002855157398639321286264516615178443430043844610000000",
         "approximateArrivalTimestamp":1672443375913,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiI0NDc1MDYyZC0wYmIzLTQ4NDEtODllYi04NDNiNmI5NTdiMTYiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM3NTI2MSwiS2V5cyI6eyJpZCI6eyJTIjoiQ1BGUiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMSJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJ3aW5fY291bnRlciI6eyJOIjoiMCJ9LCJyb2xscyI6eyJMIjpbXX0sIm91dGNvbWUiOnsiUyI6IiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJtcl9lbGV2ZW4iOnsiUyI6IiJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiTkVXX1JPVU5EIn0sImxhc3RfYWN0aW9uX2J5Ijp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImlkIjp7IlMiOiJDUEZSIn0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzY6MDcuOTM1ODY0KzAwOjAwIn19LCJPbGRJbWFnZSI6eyJ2ZXJzaW9uIjp7Ik4iOiIwIn0sInBsYXllcnMiOnsiTCI6W3siTSI6eyJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJmaW5pc2hlZCI6eyJCT09MIjpmYWxzZX0sImlkIjp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sIndpbl9jb3VudGVyIjp7Ik4iOiIwIn0sInJvbGxzIjp7IkwiOltdfSwib3V0Y29tZSI6eyJTIjoiIn19fV19LCJyb3VuZF9maW5pc2hlZCI6eyJCT09MIjp0cnVlfSwibXJfZWxldmVuIjp7IlMiOiIifSwibGFzdF9hY3Rpb24iOnsiUyI6IkNSRUFURV9HQU1FIn0sImxhc3RfYWN0aW9uX2J5Ijp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImlkIjp7IlMiOiJDUEZSIn0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzY6MDcuOTM1ODY0KzAwOjAwIn19LCJTaXplQnl0ZXMiOjQ0MX0sImV2ZW50U291cmNlIjoiYXdzOmR5bmFtb2RiIn0=",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286264516615178443430043844610",
            "subsequenceNumber":0,
            "partitionKey":"514F6C95D3B4A0F12008B5B9563BFE6D",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443375913
         }
      },
      {
         "recordId":"49636604002855157398639321286265725540998058334096457730000000",
         "approximateArrivalTimestamp":1672443379927,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJhMDM3ODY4Ny1hZTdjLTQ1ZDQtODZkNC0wNTgyODM0NGJmYmEiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM3OTc5MiwiS2V5cyI6eyJpZCI6eyJTIjoiQ1BGUiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sImlkIjp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sIndpbl9jb3VudGVyIjp7Ik4iOiIxIn0sInJvbGxzIjp7IkwiOlt7Ik0iOnsiZGljZSI6eyJMIjpbeyJNIjp7InZhbHVlIjp7Ik4iOiIzIn0sImlkIjp7IlMiOiJENiJ9fX0seyJNIjp7InZhbHVlIjp7Ik4iOiI1In0sImlkIjp7IlMiOiJENiJ9fX1dfX19XX0sIm91dGNvbWUiOnsiUyI6IldJTk5FUiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sIm1yX2VsZXZlbiI6eyJTIjoiIn0sImxhc3RfYWN0aW9uIjp7IlMiOiJST0xMX0RJQ0UifSwibGFzdF9hY3Rpb25fYnkiOnsiUyI6ImQtOVo5ZnBweXdNQ0lsdz0ifSwiaWQiOnsiUyI6IkNQRlIifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMi0xMi0zMCAyMzozNjowNy45MzU4NjQrMDA6MDAifX0sIk9sZEltYWdlIjp7InZlcnNpb24iOnsiTiI6IjEifSwicGxheWVycyI6eyJMIjpbeyJNIjp7Im5pY2tuYW1lIjp7IlMiOiJOaWNrIn0sImZpbmlzaGVkIjp7IkJPT0wiOmZhbHNlfSwiaWQiOnsiUyI6ImQtOVo5ZnBweXdNQ0lsdz0ifSwid2luX2NvdW50ZXIiOnsiTiI6IjAifSwicm9sbHMiOnsiTCI6W119LCJvdXRjb21lIjp7IlMiOiIifX19XX0sInJvdW5kX2ZpbmlzaGVkIjp7IkJPT0wiOmZhbHNlfSwibXJfZWxldmVuIjp7IlMiOiIifSwibGFzdF9hY3Rpb24iOnsiUyI6Ik5FV19ST1VORCJ9LCJsYXN0X2FjdGlvbl9ieSI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJpZCI6eyJTIjoiQ1BGUiJ9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIyLTEyLTMwIDIzOjM2OjA3LjkzNTg2NCswMDowMCJ9fSwiU2l6ZUJ5dGVzIjo0OTN9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286265725540998058334096457730",
            "subsequenceNumber":0,
            "partitionKey":"514F6C95D3B4A0F12008B5B9563BFE6D",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443379927
         }
      },
      {
         "recordId":"49636604002855157398639321286266934466817673306868547586000000",
         "approximateArrivalTimestamp":1672443384943,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJmMTJjMWZiOC0yM2ZiLTRmZjctODBhNi0yOGM1NzkyM2FmMDkiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM4NDA2OSwiS2V5cyI6eyJpZCI6eyJTIjoiQ1BGUiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMyJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJ3aW5fY291bnRlciI6eyJOIjoiMSJ9LCJyb2xscyI6eyJMIjpbXX0sIm91dGNvbWUiOnsiUyI6IiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJtcl9lbGV2ZW4iOnsiUyI6IiJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiTkVXX1JPVU5EIn0sImxhc3RfYWN0aW9uX2J5Ijp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImlkIjp7IlMiOiJDUEZSIn0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzY6MDcuOTM1ODY0KzAwOjAwIn19LCJPbGRJbWFnZSI6eyJ2ZXJzaW9uIjp7Ik4iOiIyIn0sInBsYXllcnMiOnsiTCI6W3siTSI6eyJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJmaW5pc2hlZCI6eyJCT09MIjp0cnVlfSwiaWQiOnsiUyI6ImQtOVo5ZnBweXdNQ0lsdz0ifSwid2luX2NvdW50ZXIiOnsiTiI6IjEifSwicm9sbHMiOnsiTCI6W3siTSI6eyJkaWNlIjp7IkwiOlt7Ik0iOnsidmFsdWUiOnsiTiI6IjMifSwiaWQiOnsiUyI6IkQ2In19fSx7Ik0iOnsidmFsdWUiOnsiTiI6IjUifSwiaWQiOnsiUyI6IkQ2In19fV19fX1dfSwib3V0Y29tZSI6eyJTIjoiV0lOTkVSIn19fV19LCJyb3VuZF9maW5pc2hlZCI6eyJCT09MIjp0cnVlfSwibXJfZWxldmVuIjp7IlMiOiIifSwibGFzdF9hY3Rpb24iOnsiUyI6IlJPTExfRElDRSJ9LCJsYXN0X2FjdGlvbl9ieSI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJpZCI6eyJTIjoiQ1BGUiJ9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIyLTEyLTMwIDIzOjM2OjA3LjkzNTg2NCswMDowMCJ9fSwiU2l6ZUJ5dGVzIjo0OTR9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286266934466817673306868547586",
            "subsequenceNumber":0,
            "partitionKey":"514F6C95D3B4A0F12008B5B9563BFE6D",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443384943
         }
      },
      {
         "recordId":"49636604002855157398639321286268143392637288348360114178000000",
         "approximateArrivalTimestamp":1672443390967,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiI4OTQ4NDBiMC1lNTJkLTQzNzMtYmE2My0zYjJmYTEzOGJmZmYiLCJldmVudE5hbWUiOiJSRU1PVkUiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM5MDQ4OCwiS2V5cyI6eyJpZCI6eyJTIjoiQ1BGUiJ9fSwiT2xkSW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMyJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9LCJ3aW5fY291bnRlciI6eyJOIjoiMSJ9LCJyb2xscyI6eyJMIjpbXX0sIm91dGNvbWUiOnsiUyI6IiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJtcl9lbGV2ZW4iOnsiUyI6IiJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiTkVXX1JPVU5EIn0sImxhc3RfYWN0aW9uX2J5Ijp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImlkIjp7IlMiOiJDUEZSIn0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzY6MDcuOTM1ODY0KzAwOjAwIn19LCJTaXplQnl0ZXMiOjIyNH0sImV2ZW50U291cmNlIjoiYXdzOmR5bmFtb2RiIn0=",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286268143392637288348360114178",
            "subsequenceNumber":0,
            "partitionKey":"514F6C95D3B4A0F12008B5B9563BFE6D",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443390967
         }
      },
      {
         "recordId":"49636604002855157398639321286269352318456902977534820354000000",
         "approximateArrivalTimestamp":1672443391326,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJlNDUxMzc3Yy1jNDNkLTQ3NDUtYjNlZS0xY2FhYWY0NzAyZmYiLCJldmVudE5hbWUiOiJSRU1PVkUiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjQ0MzM5MDQ4OCwiS2V5cyI6eyJpZCI6eyJTIjoiZC05WjlmcHB5d01DSWx3PSJ9fSwiT2xkSW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiU0VUX05JQ0tOQU1FIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJkLTlaOWZwcHl3TUNJbHc9In0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjItMTItMzAgMjM6MzU6NTMuNjYwMTQyKzAwOjAwIn0sImdhbWVfaWQiOnsiUyI6IkNQRlIifX0sIlNpemVCeXRlcyI6MTQ0fSwiZXZlbnRTb3VyY2UiOiJhd3M6ZHluYW1vZGIifQ==",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636604002855157398639321286269352318456902977534820354",
            "subsequenceNumber":0,
            "partitionKey":"3077CF05FAE4106AE15DE489A4BEDD9E",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672443391326
         }
      }
   ]
}
, None)
