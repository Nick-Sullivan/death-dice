import boto3
import json
import os
import itertools

session = boto3.Session()
sqs = session.client('sqs')

MESSAGES_PER_BATCH = 10  # max 10


def extract(event, context):
   print(event)
   print(f"Uploading {len(event['Records'])} records to SQS")

   batches = grouper(event['Records'], MESSAGES_PER_BATCH)

   for batch in batches:

      entries = []
      for record in batch:
         entries.append({
            'Id': record['eventID'],
            'MessageBody': json.dumps(record),
         })

      sqs.send_message_batch(
         QueueUrl=os.environ['QUEUE_URL'],
         Entries=entries
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
  os.environ['QUEUE_URL'] = "https://sqs.ap-southeast-2.amazonaws.com/314077822992/DeathDiceStage-Extract"
  extract(
    {'Records': [{'eventID': '7339c6655ded8369a025a525b05dd56a', 'eventName': 'MODIFY', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'ap-southeast-2', 'dynamodb': {'ApproximateCreationDateTime': 1672897409.0, 'Keys': {'id': {'S': 'UTEE'}}, 'NewImage': {'round_finished': {'BOOL': False}, 'players': {'L': [{'M': {'win_counter': {'N': '0'}, 'nickname': {'S': 'Nick'}, 'finished': {'BOOL': False}, 'id': {'S': 'eQR5yfzJywMCFWQ='}, 'rolls': {'L': []}, 'outcome': {'S': ''}}}]}, 'modified_by': {'S': 'eQR5yfzJywMCFWQ='}, 'modified_action': {'S': 'NEW_ROUND'}, 'id': {'S': 'UTEE'}, 'modified_at': {'S': '2023-01-05 05:43:29.426828'}, 'version': {'N': '1'}, 'table': {'S': 'Game'}, 'mr_eleven': {'S': ''}}, 'OldImage': {'round_finished': {'BOOL': True}, 'players': {'L': [{'M': {'win_counter': {'N': '0'}, 'nickname': {'S': 'Nick'}, 'finished': {'BOOL': False}, 'id': {'S': 'eQR5yfzJywMCFWQ='}, 'rolls': {'L': []}, 'outcome': {'S': ''}}}]}, 'modified_by': {'S': 'eQR5yfzJywMCFWQ='}, 'modified_action': {'S': 'CREATE_GAME'}, 'id': {'S': 'UTEE'}, 'modified_at': {'S': '2023-01-05 05:43:27.508841'}, 'version': {'N': '0'}, 'table': {'S': 'Game'}, 'mr_eleven': {'S': ''}}, 'SequenceNumber': '500000000005990453139', 'SizeBytes': 451, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'eventSourceARN': 'arn:aws:dynamodb:ap-southeast-2:314077822992:table/DeathDiceStage/stream/2023-01-05T05:17:16.783'}, {'eventID': '8ee67936dfc6f0ee8819ceae4f487d7c', 'eventName': 'MODIFY', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'ap-southeast-2', 'dynamodb': {'ApproximateCreationDateTime': 1672897411.0, 'Keys': {'id': {'S': 'UTEE'}}, 'NewImage': {'round_finished': {'BOOL': True}, 'players': {'L': [{'M': {'win_counter': {'N': '1'}, 'nickname': {'S': 'Nick'}, 'finished': {'BOOL': True}, 'id': {'S': 'eQR5yfzJywMCFWQ='}, 'rolls': {'L': [{'M': {'dice': {'L': [{'M': {'is_death_dice': {'BOOL': False}, 'id': {'S': 'D6'}, 'value': {'N': '1'}}}, {'M': {'is_death_dice': {'BOOL': False}, 'id': {'S': 'D6'}, 'value': {'N': '3'}}}]}}}]}, 'outcome': {'S': 'WINNER'}}}]}, 'modified_by': {'S': 'eQR5yfzJywMCFWQ='}, 'modified_action': {'S': 'ROLL_DICE'}, 'id': {'S': 'UTEE'}, 'modified_at': {'S': '2023-01-05 05:43:30.909262'}, 'version': {'N': '2'}, 'table': {'S': 'Game'}, 'mr_eleven': {'S': ''}}, 'OldImage': {'round_finished': {'BOOL': False}, 'players': {'L': [{'M': {'win_counter': {'N': '0'}, 'nickname': {'S': 'Nick'}, 'finished': {'BOOL': False}, 'id': {'S': 'eQR5yfzJywMCFWQ='}, 'rolls': {'L': []}, 'outcome': {'S': ''}}}]}, 'modified_by': {'S': 'eQR5yfzJywMCFWQ='}, 'modified_action': {'S': 'NEW_ROUND'}, 'id': {'S': 'UTEE'}, 'modified_at': {'S': '2023-01-05 05:43:29.426828'}, 'version': {'N': '1'}, 'table': {'S': 'Game'}, 'mr_eleven': {'S': ''}}, 'SequenceNumber': '600000000005990454001', 'SizeBytes': 533, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'eventSourceARN': 'arn:aws:dynamodb:ap-southeast-2:314077822992:table/DeathDiceStage/stream/2023-01-05T05:17:16.783'}, {'eventID': '3dd4c6c113b6240f8a77f153c781b059', 'eventName': 'REMOVE', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'ap-southeast-2', 'dynamodb': {'ApproximateCreationDateTime': 1672897412.0, 'Keys': {'id': {'S': 'eQR5yfzJywMCFWQ='}}, 'OldImage': {'account_id': {'NULL': True}, 'nickname': {'S': 'Nick'}, 'modified_action': {'S': 'JOIN_GAME'}, 'id': {'S': 'eQR5yfzJywMCFWQ='}, 'modified_at': {'S': '2023-01-05 05:43:27.508604'}, 'version': {'N': '2'}, 'table': {'S': 'Connection'}, 'game_id': {'S': 'UTEE'}}, 'SequenceNumber': '700000000005990455052', 'SizeBytes': 155, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'eventSourceARN': 'arn:aws:dynamodb:ap-southeast-2:314077822992:table/DeathDiceStage/stream/2023-01-05T05:17:16.783'}, {'eventID': 'f92a8dd0a7e515c76f8774c3198c149b', 'eventName': 'REMOVE', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'ap-southeast-2', 'dynamodb': {'ApproximateCreationDateTime': 1672897412.0, 'Keys': {'id': {'S': 'UTEE'}}, 'OldImage': {'round_finished': {'BOOL': True}, 'players': {'L': [{'M': {'win_counter': {'N': '1'}, 'nickname': {'S': 'Nick'}, 'finished': {'BOOL': True}, 'id': {'S': 'eQR5yfzJywMCFWQ='}, 'rolls': {'L': [{'M': {'dice': {'L': [{'M': {'is_death_dice': {'BOOL': False}, 'id': {'S': 'D6'}, 'value': {'N': '1'}}}, {'M': {'is_death_dice': {'BOOL': False}, 'id': {'S': 'D6'}, 'value': {'N': '3'}}}]}}}]}, 'outcome': {'S': 'WINNER'}}}]}, 'modified_by': {'S': 'eQR5yfzJywMCFWQ='}, 'modified_action': {'S': 'ROLL_DICE'}, 'id': {'S': 'UTEE'}, 'modified_at': {'S': '2023-01-05 05:43:30.909262'}, 'version': {'N': '2'}, 'table': {'S': 'Game'}, 'mr_eleven': {'S': ''}}, 'SequenceNumber': '800000000005990455053', 'SizeBytes': 311, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'eventSourceARN': 'arn:aws:dynamodb:ap-southeast-2:314077822992:table/DeathDiceStage/stream/2023-01-05T05:17:16.783'}]}
   ,None
  )

  