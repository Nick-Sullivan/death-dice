# Called by Kinesis 
# https://docs.aws.amazon.com/kinesisanalytics/latest/dev/lambda-preprocessing.html

import base64
import json
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

deserialiser = TypeDeserializer()


def extract(event, context):
  """Converts DynamoDB diff streams into files to be stored in s3"""
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
   "invocationId":"bd46d7d6-fce9-44e6-b918-8f6c39a52ae4",
   "sourceKinesisStreamArn":"arn:aws:kinesis:ap-southeast-2:314077822992:stream/DeathDiceStage",
   "deliveryStreamArn":"arn:aws:firehose:ap-southeast-2:314077822992:deliverystream/DeathDiceStage",
   "region":"ap-southeast-2",
   "records":[
      {
         "recordId":"49636633817702646102964746676780538356721397016536547330000000",
         "approximateArrivalTimestamp":1672535312040,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJjZThjYjE4Ni1jNTBhLTRmODYtYjM0Ni0xNTc1OTY0YWE2Y2QiLCJldmVudE5hbWUiOiJJTlNFUlQiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMxMTE3MywiS2V5cyI6eyJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMCJ9LCJuaWNrbmFtZSI6eyJOVUxMIjp0cnVlfSwibGFzdF9hY3Rpb24iOnsiUyI6IkNSRUFURV9DT05ORUNUSU9OIn0sInRhYmxlIjp7IlMiOiJDb25uZWN0aW9uIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjMtMDEtMDEgMDE6MDg6MzAuOTUxODQyKzAwOjAwIn0sImdhbWVfaWQiOnsiTlVMTCI6dHJ1ZX19LCJTaXplQnl0ZXMiOjE1N30sImV2ZW50U291cmNlIjoiYXdzOmR5bmFtb2RiIn0=",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676780538356721397016536547330",
            "subsequenceNumber":0,
            "partitionKey":"8C6A3D0A6C1FD90D0364355DA3D16045",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535312040
         }
      },
      {
         "recordId":"49636633817702646102964746676781747282541011851869683714000000",
         "approximateArrivalTimestamp":1672535315065,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJhYzc1MjliNy1lOWNiLTQ1NjgtYTYxNi1mNTlmYmI2NDNiNmMiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMxNDgyMiwiS2V5cyI6eyJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMSJ9LCJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiU0VUX05JQ0tOQU1FIn0sInRhYmxlIjp7IlMiOiJDb25uZWN0aW9uIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjMtMDEtMDEgMDE6MDg6MzAuOTUxODQyKzAwOjAwIn0sImdhbWVfaWQiOnsiTlVMTCI6dHJ1ZX19LCJPbGRJbWFnZSI6eyJ2ZXJzaW9uIjp7Ik4iOiIwIn0sIm5pY2tuYW1lIjp7Ik5VTEwiOnRydWV9LCJsYXN0X2FjdGlvbiI6eyJTIjoiQ1JFQVRFX0NPTk5FQ1RJT04ifSwidGFibGUiOnsiUyI6IkNvbm5lY3Rpb24ifSwiYWNjb3VudF9pZCI6eyJOVUxMIjp0cnVlfSwiaWQiOnsiUyI6ImVDZDZTZTZfU3dNQ0V6QT0ifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMy0wMS0wMSAwMTowODozMC45NTE4NDIrMDA6MDAifSwiZ2FtZV9pZCI6eyJOVUxMIjp0cnVlfX0sIlNpemVCeXRlcyI6Mjk1fSwiZXZlbnRTb3VyY2UiOiJhd3M6ZHluYW1vZGIifQ==",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676781747282541011851869683714",
            "subsequenceNumber":0,
            "partitionKey":"8C6A3D0A6C1FD90D0364355DA3D16045",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535315065
         }
      },
      {
         "recordId":"49636633817702646102964746676782956208360626549763866626000000",
         "approximateArrivalTimestamp":1672535317040,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJiMDRiNGM3YS02OTIwLTQzYWEtOTJjZi03MWEyN2YxYjg3NTYiLCJldmVudE5hbWUiOiJJTlNFUlQiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMxNjU0OCwiS2V5cyI6eyJpZCI6eyJTIjoiRk9UQiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMCJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9LCJ3aW5fY291bnRlciI6eyJOIjoiMCJ9LCJyb2xscyI6eyJMIjpbXX0sIm91dGNvbWUiOnsiUyI6IiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sIm1yX2VsZXZlbiI6eyJTIjoiIn0sImxhc3RfYWN0aW9uIjp7IlMiOiJDUkVBVEVfR0FNRSJ9LCJ0YWJsZSI6eyJTIjoiR2FtZSJ9LCJsYXN0X2FjdGlvbl9ieSI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9LCJpZCI6eyJTIjoiRk9UQiJ9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIzLTAxLTAxIDAxOjA4OjM2LjQ3MzY1NyswMDowMCJ9fSwiU2l6ZUJ5dGVzIjoyMzN9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676782956208360626549763866626",
            "subsequenceNumber":0,
            "partitionKey":"B2CCB88B721425970AB23A831CDAC9A1",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535317040
         }
      },
      {
         "recordId":"49636633817702646102964746676784165134180241178938572802000000",
         "approximateArrivalTimestamp":1672535317078,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiI0MGU1ZmRjZC01OTIxLTQwM2QtYTUwYy1kNDE5ZjY3NGExZTMiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMxNjU1OCwiS2V5cyI6eyJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiSk9JTl9HQU1FIn0sInRhYmxlIjp7IlMiOiJDb25uZWN0aW9uIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sImdhbWVfaWQiOnsiUyI6IkZPVEIifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMy0wMS0wMSAwMTowODozMC45NTE4NDIrMDA6MDAifX0sIk9sZEltYWdlIjp7InZlcnNpb24iOnsiTiI6IjEifSwibmlja25hbWUiOnsiUyI6Ik5pY2sifSwibGFzdF9hY3Rpb24iOnsiUyI6IlNFVF9OSUNLTkFNRSJ9LCJ0YWJsZSI6eyJTIjoiQ29ubmVjdGlvbiJ9LCJhY2NvdW50X2lkIjp7Ik5VTEwiOnRydWV9LCJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9LCJnYW1lX2lkIjp7Ik5VTEwiOnRydWV9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIzLTAxLTAxIDAxOjA4OjMwLjk1MTg0MiswMDowMCJ9fSwiU2l6ZUJ5dGVzIjoyOTR9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676784165134180241178938572802",
            "subsequenceNumber":0,
            "partitionKey":"8C6A3D0A6C1FD90D0364355DA3D16045",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535317078
         }
      },
      {
         "recordId":"49636633817702646102964746676785374059999856082991185922000000",
         "approximateArrivalTimestamp":1672535320054,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiI3YzU4OGJmMy01ZmU0LTRhZWYtYWRjOS04MWRjNGJhMDZhZmEiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMxOTM5NCwiS2V5cyI6eyJpZCI6eyJTIjoiRk9UQiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMSJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9LCJ3aW5fY291bnRlciI6eyJOIjoiMCJ9LCJyb2xscyI6eyJMIjpbXX0sIm91dGNvbWUiOnsiUyI6IiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6ZmFsc2V9LCJtcl9lbGV2ZW4iOnsiUyI6IiJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiTkVXX1JPVU5EIn0sInRhYmxlIjp7IlMiOiJHYW1lIn0sImxhc3RfYWN0aW9uX2J5Ijp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sImlkIjp7IlMiOiJGT1RCIn0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjMtMDEtMDEgMDE6MDg6MzYuNDczNjU3KzAwOjAwIn19LCJPbGRJbWFnZSI6eyJ2ZXJzaW9uIjp7Ik4iOiIwIn0sInBsYXllcnMiOnsiTCI6W3siTSI6eyJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJmaW5pc2hlZCI6eyJCT09MIjpmYWxzZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sIndpbl9jb3VudGVyIjp7Ik4iOiIwIn0sInJvbGxzIjp7IkwiOltdfSwib3V0Y29tZSI6eyJTIjoiIn19fV19LCJyb3VuZF9maW5pc2hlZCI6eyJCT09MIjp0cnVlfSwibXJfZWxldmVuIjp7IlMiOiIifSwibGFzdF9hY3Rpb24iOnsiUyI6IkNSRUFURV9HQU1FIn0sInRhYmxlIjp7IlMiOiJHYW1lIn0sImxhc3RfYWN0aW9uX2J5Ijp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sImlkIjp7IlMiOiJGT1RCIn0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjMtMDEtMDEgMDE6MDg6MzYuNDczNjU3KzAwOjAwIn19LCJTaXplQnl0ZXMiOjQ1OX0sImV2ZW50U291cmNlIjoiYXdzOmR5bmFtb2RiIn0=",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676785374059999856082991185922",
            "subsequenceNumber":0,
            "partitionKey":"B2CCB88B721425970AB23A831CDAC9A1",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535320054
         }
      },
      {
         "recordId":"49636633817702646102964746676786582985819470849604845570000000",
         "approximateArrivalTimestamp":1672535323065,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiIwNzMwYTY0OC04OWViLTRhYjktOTkzZS0zNTQ1ZWJkOWRlNDIiLCJldmVudE5hbWUiOiJNT0RJRlkiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMyMjEyMSwiS2V5cyI6eyJpZCI6eyJTIjoiRk9UQiJ9fSwiTmV3SW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sIndpbl9jb3VudGVyIjp7Ik4iOiIxIn0sInJvbGxzIjp7IkwiOlt7Ik0iOnsiZGljZSI6eyJMIjpbeyJNIjp7InZhbHVlIjp7Ik4iOiIxIn0sImlkIjp7IlMiOiJENiJ9fX0seyJNIjp7InZhbHVlIjp7Ik4iOiIyIn0sImlkIjp7IlMiOiJENiJ9fX1dfX19XX0sIm91dGNvbWUiOnsiUyI6IldJTk5FUiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sIm1yX2VsZXZlbiI6eyJTIjoiIn0sImxhc3RfYWN0aW9uIjp7IlMiOiJST0xMX0RJQ0UifSwidGFibGUiOnsiUyI6IkdhbWUifSwibGFzdF9hY3Rpb25fYnkiOnsiUyI6ImVDZDZTZTZfU3dNQ0V6QT0ifSwiaWQiOnsiUyI6IkZPVEIifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMy0wMS0wMSAwMTowODozNi40NzM2NTcrMDA6MDAifX0sIk9sZEltYWdlIjp7InZlcnNpb24iOnsiTiI6IjEifSwicGxheWVycyI6eyJMIjpbeyJNIjp7Im5pY2tuYW1lIjp7IlMiOiJOaWNrIn0sImZpbmlzaGVkIjp7IkJPT0wiOmZhbHNlfSwiaWQiOnsiUyI6ImVDZDZTZTZfU3dNQ0V6QT0ifSwid2luX2NvdW50ZXIiOnsiTiI6IjAifSwicm9sbHMiOnsiTCI6W119LCJvdXRjb21lIjp7IlMiOiIifX19XX0sInJvdW5kX2ZpbmlzaGVkIjp7IkJPT0wiOmZhbHNlfSwibXJfZWxldmVuIjp7IlMiOiIifSwibGFzdF9hY3Rpb24iOnsiUyI6Ik5FV19ST1VORCJ9LCJ0YWJsZSI6eyJTIjoiR2FtZSJ9LCJsYXN0X2FjdGlvbl9ieSI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9LCJpZCI6eyJTIjoiRk9UQiJ9LCJjcmVhdGVkX29uIjp7IlMiOiIyMDIzLTAxLTAxIDAxOjA4OjM2LjQ3MzY1NyswMDowMCJ9fSwiU2l6ZUJ5dGVzIjo1MTF9LCJldmVudFNvdXJjZSI6ImF3czpkeW5hbW9kYiJ9",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676786582985819470849604845570",
            "subsequenceNumber":0,
            "partitionKey":"B2CCB88B721425970AB23A831CDAC9A1",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535323065
         }
      },
      {
         "recordId":"49636633817702646102964746676787791911639085616218505218000000",
         "approximateArrivalTimestamp":1672535325075,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiJiNzEwYTNlZC1lNGE2LTQwNTUtODhjZS01ZWMzZTUxYjBiMzMiLCJldmVudE5hbWUiOiJSRU1PVkUiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMyNDEyMywiS2V5cyI6eyJpZCI6eyJTIjoiRk9UQiJ9fSwiT2xkSW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJwbGF5ZXJzIjp7IkwiOlt7Ik0iOnsibmlja25hbWUiOnsiUyI6Ik5pY2sifSwiZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sIndpbl9jb3VudGVyIjp7Ik4iOiIxIn0sInJvbGxzIjp7IkwiOlt7Ik0iOnsiZGljZSI6eyJMIjpbeyJNIjp7InZhbHVlIjp7Ik4iOiIxIn0sImlkIjp7IlMiOiJENiJ9fX0seyJNIjp7InZhbHVlIjp7Ik4iOiIyIn0sImlkIjp7IlMiOiJENiJ9fX1dfX19XX0sIm91dGNvbWUiOnsiUyI6IldJTk5FUiJ9fX1dfSwicm91bmRfZmluaXNoZWQiOnsiQk9PTCI6dHJ1ZX0sIm1yX2VsZXZlbiI6eyJTIjoiIn0sImxhc3RfYWN0aW9uIjp7IlMiOiJST0xMX0RJQ0UifSwidGFibGUiOnsiUyI6IkdhbWUifSwibGFzdF9hY3Rpb25fYnkiOnsiUyI6ImVDZDZTZTZfU3dNQ0V6QT0ifSwiaWQiOnsiUyI6IkZPVEIifSwiY3JlYXRlZF9vbiI6eyJTIjoiMjAyMy0wMS0wMSAwMTowODozNi40NzM2NTcrMDA6MDAifX0sIlNpemVCeXRlcyI6Mjg1fSwiZXZlbnRTb3VyY2UiOiJhd3M6ZHluYW1vZGIifQ==",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676787791911639085616218505218",
            "subsequenceNumber":0,
            "partitionKey":"B2CCB88B721425970AB23A831CDAC9A1",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535325075
         }
      },
      {
         "recordId":"49636633817702646102964746676789000837458700245393211394000000",
         "approximateArrivalTimestamp":1672535325110,
         "data":"eyJhd3NSZWdpb24iOiJhcC1zb3V0aGVhc3QtMiIsImV2ZW50SUQiOiI0YjFlNGQ0MC1hNTk0LTQwNmMtYjgxYy1mZWQ2YmY3ZmUxMGUiLCJldmVudE5hbWUiOiJSRU1PVkUiLCJ1c2VySWRlbnRpdHkiOm51bGwsInJlY29yZEZvcm1hdCI6ImFwcGxpY2F0aW9uL2pzb24iLCJ0YWJsZU5hbWUiOiJEZWF0aERpY2VTdGFnZSIsImR5bmFtb2RiIjp7IkFwcHJveGltYXRlQ3JlYXRpb25EYXRlVGltZSI6MTY3MjUzNTMyNDEyMywiS2V5cyI6eyJpZCI6eyJTIjoiZUNkNlNlNl9Td01DRXpBPSJ9fSwiT2xkSW1hZ2UiOnsidmVyc2lvbiI6eyJOIjoiMiJ9LCJuaWNrbmFtZSI6eyJTIjoiTmljayJ9LCJsYXN0X2FjdGlvbiI6eyJTIjoiSk9JTl9HQU1FIn0sInRhYmxlIjp7IlMiOiJDb25uZWN0aW9uIn0sImFjY291bnRfaWQiOnsiTlVMTCI6dHJ1ZX0sImlkIjp7IlMiOiJlQ2Q2U2U2X1N3TUNFekE9In0sImNyZWF0ZWRfb24iOnsiUyI6IjIwMjMtMDEtMDEgMDE6MDg6MzAuOTUxODQyKzAwOjAwIn0sImdhbWVfaWQiOnsiUyI6IkZPVEIifX0sIlNpemVCeXRlcyI6MTU2fSwiZXZlbnRTb3VyY2UiOiJhd3M6ZHluYW1vZGIifQ==",
         "kinesisRecordMetadata":{
            "sequenceNumber":"49636633817702646102964746676789000837458700245393211394",
            "subsequenceNumber":0,
            "partitionKey":"8C6A3D0A6C1FD90D0364355DA3D16045",
            "shardId":"shardId-000000000000",
            "approximateArrivalTimestamp":1672535325110
         }
      }
   ]
}
, None)
