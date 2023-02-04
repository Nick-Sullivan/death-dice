
from client_interactor import lambda_handler


@lambda_handler
def heartbeat(connection_id, request):
  return


if __name__ == '__main__':
  heartbeat({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
