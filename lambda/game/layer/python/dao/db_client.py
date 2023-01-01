"""Single instance of DynamoDB connection, to reduce connection overhead"""
import boto3

client = boto3.client('dynamodb', region_name='ap-southeast-2')

def get_client():
  return client
