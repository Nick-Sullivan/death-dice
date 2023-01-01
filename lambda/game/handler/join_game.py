"""All functions in are lambda entry points"""

from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, GameNotFoundException, TransactionWriter, concurrency_retry
from model import ConnectionAction, GameAction, GameState, Player, RollResultNote

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()
game_dao = GameDao()


@lambda_handler
def join_game(connection_id, request):
  """Called by the WebSocketAPI when a player wants to join an existing game"""

  game_id = request['data'].upper()

  connection = connection_dao.get(connection_id)

  try:

    game = _join_game(connection, game_id)

    client_notifier.send_notification([connection_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    client_notifier.send_game_state_update(game)

  except GameNotFoundException:
    client_notifier.send_notification([connection_id], {
      'action': 'joinGame',
      'error': f'Unable to join game: {game_id}',
    })


@concurrency_retry
def _join_game(connection, game_id) -> GameState:

  game = game_dao.get(game_id)
  game.modified_action = GameAction.JOIN_GAME
  game.modified_by = connection.id
  
  connection.game_id = game_id
  connection.modified_action = ConnectionAction.JOIN_GAME
  
  game.players.append(Player(
    id=connection.id,
    nickname=connection.nickname,
    win_counter=0,
    finished=False,
    outcome=RollResultNote.NONE,
    rolls=[]
  ))

  with TransactionWriter() as transaction:
    connection_dao.set(connection, transaction)
    game_dao.set(game, transaction)

  return game


if __name__ == '__main__':
  import json
  join_game({
    'requestContext': {
      'connectionId': 'petes_connection_id'
    },
    'body': json.dumps({'data': 'YBMI'})
  }, None)
