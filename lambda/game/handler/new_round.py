"""All functions in are lambda entry points"""

from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, concurrency_retry
from model import GameAction, GameState, RollResultNote

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()
game_dao = GameDao()


@lambda_handler
def new_round(connection_id, request):
  """Called by the WebSocketAPI when a player wants to start the next round"""

  connection = connection_dao.get(connection_id)
  
  game = _new_round(connection)
  
  client_notifier.send_game_state_update(game)


@concurrency_retry
def _new_round(connection) -> GameState:

  game = game_dao.get(connection.game_id)

  if not game.round_finished:
    return game

  game.round_id += 1
  game.round_finished = False
  game.modified_action = GameAction.NEW_ROUND
  game.modified_by = connection.id

  for player in game.players:
    player.outcome = RollResultNote.NONE
    player.finished = False
    player.rolls = []

  game_dao.set(game)

  return game


if __name__ == '__main__':
  new_round({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
