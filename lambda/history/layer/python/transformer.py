import json
from boto3.dynamodb.types import TypeDeserializer
from collections import defaultdict
from dataclasses import dataclass
from dateutil import parser
from decimal import Decimal


@dataclass
class TransformedMessageGroup:
   table_name: str
   date_id: str
   events: list[dict]


class MessageTransformer:
   deserialiser = TypeDeserializer()

   def load_messages(self, messages) -> None:
      self.file_values = defaultdict(list)
      for sqs_event in messages:
         dynamodb_event = json.loads(sqs_event['Body'])
         
         transformed = self.transform_event(dynamodb_event)

         key = (transformed['table'], transformed['date_id'])
         self.file_values[key].append(transformed)

      self.transformed_message_groups = []
      for (table_name, date_id), events in self.file_values.items():
         sorted(events, key=lambda x: x['modified_at'])
         self.transformed_message_groups.append(TransformedMessageGroup(
            table_name=table_name,
            date_id=date_id,
            events=events,
         ))

   def get_transformed_messages(self) -> TransformedMessageGroup:
      return self.transformed_message_groups

   def get_unique_date_ids(self) -> set[str]:
      return {g.date_id for g in self.transformed_message_groups}
      
   @classmethod
   def transform_event(cls, event) -> dict:
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
         response[key] = cls.deserialiser.deserialize(value)

      response = cls.remove_decimals(response)

      date = parser.parse(response['modified_at'])
      response['date_id'] = date.strftime('%Y-%m-%d')

      return response

   @classmethod
   def remove_decimals(cls, key_values) -> dict:
      for key, value in key_values.items():
         if isinstance(value, Decimal):
            key_values[key] = int(value)

         elif isinstance(value, dict):
            key_values[key] = cls.remove_decimals(value)
         
         elif isinstance(value, list):
            key_values[key] = [cls.remove_decimals(v) for v in value]

      return key_values
