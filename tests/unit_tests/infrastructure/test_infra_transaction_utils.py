import pytest
from botocore.exceptions import ClientError
from domain_services.transaction_utils import concurrency_retry


@concurrency_retry
def fake_concurrency_function(a_list):
  a_list.append('call') # count iterations with mutable argument

  if len(a_list) < 3:
    raise ClientError(
      error_response={'Error': {'Code': 'TransactionCanceledException'}},
      operation_name='operation_name',
    )
  else:
    raise Exception('Some other exception')
  

def test_concurrency_retry():
  """Three concurrency exceptions, one other exception"""
  a_list = []
  with pytest.raises(Exception):
    fake_concurrency_function(a_list)
  assert len(a_list) == 3

