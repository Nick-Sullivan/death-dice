
from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, TransactionWriter, concurrency_retry
from game_logic import calculate_turn_results
from model import GameState

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()
game_dao = GameDao()


@lambda_handler
def disconnect(connection_id, request):
  """Called by the WebSocketAPI when a connection is to be destroyed"""

  connection = connection_dao.get(connection_id)

  if connection.game_id is None:
    return connection_dao.delete(connection)

  game = _disconnect(connection)

  if game is not None:
    client_notifier.send_game_state_update(game)


@concurrency_retry
def _disconnect(connection) -> GameState:
  
  game = game_dao.get(connection.game_id)

  if len(game.players) <= 1:
    with TransactionWriter() as transaction:
      connection_dao.delete(connection, transaction)
      game_dao.delete(game, transaction)
      return None
  
  game.players = [p for p in game.players if p.id != connection.id]

  is_round_finished = all([p.finished for p in game.players])
  if is_round_finished:
    game = calculate_turn_results(game)

  with TransactionWriter() as transaction:
    connection_dao.delete(connection, transaction)
    game_dao.set(game, transaction)

  return game


if __name__ == '__main__':
  disconnect({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
