

from game_logic.roll_judge import GroupRollJudge
from model.game_items import GameState
from model.roll_result import RollResultType


def calculate_turn_results(game) -> GameState:

  player_rolls = {p.id: p.rolls for p in game.players}

  judge = GroupRollJudge(player_rolls, game.mr_eleven)
  results = judge.calculate_result()
  mr_eleven = judge.calculate_new_mr_eleven()

  game.round_finished = all([r.turn_finished for r in results.values()])
  game.mr_eleven = mr_eleven if mr_eleven is not None else ''
  
  for player in game.players:
    player.outcome = results[player.id].note
    player.finished = results[player.id].turn_finished

    if not game.round_finished:
      continue

    if results[player.id].type == RollResultType.WINNER:
      player.win_counter += 1
    elif results[player.id].type == RollResultType.LOSER:
      player.win_counter = 0

  return game

# Notifications

