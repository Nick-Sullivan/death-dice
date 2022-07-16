"""Rolls """

from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, concurrency_retry
from game_logic import DiceRoller, IndividualRollJudge, calculate_turn_results
from model import GameState

client_notifier = ClientNotifier()
connection_dao = ConnectionDao()
game_dao = GameDao()


@lambda_handler
def roll_dice(connection_id, request):
  """Called by the WebSocketAPI when a player wants to roll dice in the current round"""

  connection = connection_dao.get(connection_id)

  game = _roll_dice(connection)

  client_notifier.send_game_state_update(game)


@concurrency_retry
def _roll_dice(connection) -> GameState:

  game = game_dao.get(connection.game_id)

  player = next(p for p in game.players if p.id == connection.id)

  new_roll = DiceRoller.roll(player.rolls, player.win_counter, player.nickname)
  player.rolls.append(new_roll)

  roll_result = IndividualRollJudge.calculate_result(player.rolls, player.nickname == game.mr_eleven)
  player.finished = roll_result.turn_finished
  player.outcome = roll_result.note

  is_round_finished = all([p.finished for p in game.players])
  if is_round_finished:
    game = calculate_turn_results(game)
  
  game_dao.set(game)

  return game


if __name__ == '__main__':
  roll_dice({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
