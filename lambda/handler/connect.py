
from client_interactor import lambda_handler
from dao import ConnectionDao
from model import ConnectionItem

connection_dao = ConnectionDao()


@lambda_handler
def connect(connection_id, request):
  """Called by the WebSocketAPI when a new connection is established. Creates a new connection object."""

  connection_dao.create(ConnectionItem(id=connection_id))


if __name__ == '__main__':
  connect({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
