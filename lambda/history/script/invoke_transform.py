import boto3


if __name__ == '__main__':
   session = boto3.Session()
   client = session.client('lambda')

   client.invoke(
      FunctionName='DeathDice-Transform',
   )
   