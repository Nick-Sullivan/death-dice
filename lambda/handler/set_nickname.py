
from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()


@lambda_handler
def set_nickname(connection_id, request):
  """Called by the WebSocketAPI when a player wants to set their display name"""

  nickname = request['data']

  if not connection_dao.is_valid_nickname(nickname):
    client_notifier.send_notification(
      [connection_id], 
      {'action': 'setNickname', 'error': 'Invalid nickname'}
    )
    return

  connection = connection_dao.get(connection_id)
  connection.nickname = nickname
  connection_dao.set(connection)

  client_notifier.send_notification([connection_id], {
    'action': 'setNickname',
    'data': {
      'nickname': nickname,
      'playerId': connection_id,
    },
  })


if __name__ == '__main__':
  import json
  set_nickname({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    },
    'body': json.dumps({'data': 'nick_name'})
  }, None)
 