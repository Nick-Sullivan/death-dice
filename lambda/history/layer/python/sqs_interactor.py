import json
import itertools
import os


class SqsInteractor:
   MAX_BATCHES = 500
   MESSAGES_PER_BATCH = 10  # max 10

   def __init__(self, sqs):
      self.sqs = sqs
      self.url = os.environ['QUEUE_URL']

   def send_messages(self, messages):
      batches = grouper(messages, self.MESSAGES_PER_BATCH)

      for batch in batches:

         entries = []
         for record in batch:
            entries.append({
               'Id': record['eventID'],
               'MessageBody': json.dumps(record),
            })

         self.sqs.send_message_batch(
            QueueUrl=self.url,
            Entries=entries
         )

   def get_messages(self):
      messages = []
      self.receipts = []
      for _ in range(self.MAX_BATCHES):

         response = self.sqs.receive_message(
            QueueUrl=self.url,
            MaxNumberOfMessages=self.MESSAGES_PER_BATCH,
         )

         batch = response.get('Messages')

         if batch is None:
            break

         messages.extend(batch)

      for sqs_event in messages:
         self.receipts.append({
            'Id': sqs_event['MessageId'],
            'ReceiptHandle': sqs_event['ReceiptHandle'],
         })

      return messages

   def delete_messages(self):
      for batch in grouper(self.receipts, self.MESSAGES_PER_BATCH):
         self.sqs.delete_message_batch(
            QueueUrl=self.url,
            Entries=batch,
         )
      self.receipts = []


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
      