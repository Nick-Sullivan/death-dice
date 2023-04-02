
from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, concurrency_retry
from model import GameAction, GameState, RollResultNote, Player

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()
game_dao = GameDao()


@lambda_handler
def stop_spectating(connection_id, request):
  """Called by the WebSocketAPI when a spectator wants to rejoin the game"""

  connection = connection_dao.get(connection_id)
  
  game = _stop_spectating(connection)
  
  client_notifier.send_game_state_update(game)


@concurrency_retry
def _stop_spectating(connection) -> GameState:

  game = game_dao.get(connection.game_id)

  matching_spectators = [s for s in game.spectators if s.id == connection.id]
  if not matching_spectators:
    return game

  spectator = matching_spectators[0]

  game.modified_action = GameAction.STOP_SPECTATING
  game.modified_by = connection.id

  game.spectators.remove(spectator)

  game.players.append(Player(
    id=spectator.id,
    account_id=spectator.account_id,
    nickname=spectator.nickname,
    win_counter=0,
    finished=False,
    outcome=RollResultNote.NONE,
    rolls=[]
  ))

  game_dao.set(game)

  return game


if __name__ == '__main__':
  stop_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
