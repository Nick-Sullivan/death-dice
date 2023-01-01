
from client_interactor import lambda_handler
from dao import ConnectionDao
from model import ConnectionAction, ConnectionItem

connection_dao = ConnectionDao()


@lambda_handler
def connect(connection_id, request):
  """Called by the WebSocketAPI when a new connection is established. Creates a new connection object."""
  connection = ConnectionItem(
    id=connection_id,
    modified_action=ConnectionAction.CREATE_CONNECTION,
  )
  connection_dao.create(connection)


if __name__ == '__main__':
  connect({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
