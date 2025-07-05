from botocore.exceptions import ClientError

def concurrency_retry(func, max_attempts=30):
  """Decorator, reattempts processing if a transaction fails because the data was changed"""

  def inner(*args, **kwargs):
    attempts = 0
    while attempts < max_attempts:
      attempts += 1

      try:

        return func(*args, **kwargs)

      except ClientError as e:
        
        if e.response['Error']['Code'] == 'TransactionCanceledException':
          print('Transaction aborted')
        else:
          raise e
          
        if attempts == max_attempts:
          raise e

  return inner
