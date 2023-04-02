
from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, concurrency_retry
from game_logic import calculate_turn_results
from model import GameAction, GameState, Spectator

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()
game_dao = GameDao()


@lambda_handler
def start_spectating(connection_id, request):
  """Called by the WebSocketAPI when a player wants to start spectating the game"""

  connection = connection_dao.get(connection_id)
  
  game = _start_spectating(connection)
  
  client_notifier.send_game_state_update(game)


@concurrency_retry
def _start_spectating(connection) -> GameState:

  game = game_dao.get(connection.game_id)

  matching_players = [p for p in game.players if p.id == connection.id]
  if not matching_players:
    return game

  player = matching_players[0]

  game.modified_action = GameAction.START_SPECTATING
  game.modified_by = connection.id

  game.players.remove(player)

  game.spectators.append(Spectator(
    id=player.id,
    account_id=player.account_id,
    nickname=player.nickname
  ))

  is_round_now_finished = all([p.finished for p in game.players])
  if not game.round_finished and is_round_now_finished:
    game = calculate_turn_results(game)

  game_dao.set(game)

  return game


if __name__ == '__main__':
  start_spectating({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
