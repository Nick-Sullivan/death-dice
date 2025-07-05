
import boto3
import os

session = boto3.Session()
athena = session.client('athena')
glue = session.client('glue')


def start_query(event, context):
  print(event)

  named_query = athena.get_named_query(
    NamedQueryId=os.environ['QUERY_ID']
  )['NamedQuery']

  date_ids = event['detail']['date_ids']

  for date_id in date_ids:
    print(f'Starting query for {date_id}')

    create_partition(named_query['Database'], 'game', date_id)

    athena.start_query_execution(
      QueryString=named_query['QueryString'],
      QueryExecutionContext={
        'Database': named_query['Database']
      },
      WorkGroup=named_query['WorkGroup'],
      ExecutionParameters=[f'\'{date_id}\''],
    )['QueryExecutionId']
 

def create_partition(database, table, date_id):
  
  response = glue.get_table(
    DatabaseName=database,
    Name=table,
  )

  table_data = {}
  table_data['input_format'] = response['Table']['StorageDescriptor']['InputFormat']
  table_data['output_format'] = response['Table']['StorageDescriptor']['OutputFormat']
  table_data['table_location'] = response['Table']['StorageDescriptor']['Location']
  table_data['serde_info'] = response['Table']['StorageDescriptor']['SerdeInfo']

  location = table_data['table_location'] + f'date_id={date_id}/'

  try:
    glue.create_partition(
      DatabaseName=database,
      TableName=table,
      PartitionInput={
        'Values': [date_id],
        'StorageDescriptor': {
          'Location': location,
          'InputFormat': table_data['input_format'],
          'OutputFormat': table_data['output_format'],
          'SerdeInfo': table_data['serde_info']
        },
      },
    )
    print(f'New partition created for table {table}, date_id {date_id}')
  
  except glue.exceptions.AlreadyExistsException:
    print(f'Partition already exists for table {table}, date_id {date_id}')


if __name__ == '__main__':
   os.environ['QUERY_ID'] = '15f03723-f30b-46bc-a526-0c7dabf88479'
   start_query(
    {'version': '0', 'id': '0d8d2c02-c9d4-9f56-88a5-28c97def2ad2', 'detail-type': 'Transformation complete', 'source': 'death.dice', 'account': '314077822992', 'time': '2023-01-07T03:04:45Z', 'region': 'ap-southeast-2', 'resources': [], 'detail': {}}  # noqa: E501
    ,None
  )
