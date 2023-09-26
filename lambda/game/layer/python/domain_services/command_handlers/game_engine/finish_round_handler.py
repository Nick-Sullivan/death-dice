from dataclasses import dataclass

from domain_models import GameState, RollResultType
from domain_models.commands import CalculateGroupResultCommand, FinishRoundCommand

from ...interfaces import IMediator


@dataclass
class FinishRoundHandler:
    mediator: IMediator

    def handle(self, command: FinishRoundCommand) -> GameState:
        player_rolls = {p.id: p.rolls for p in command.game.players}

        results, mr_eleven = self.mediator.send(CalculateGroupResultCommand(player_rolls, command.game.mr_eleven))

        command.game.round_finished = all([r.turn_finished for r in results.values()])
        command.game.mr_eleven = mr_eleven if mr_eleven is not None else ''
        
        for player in command.game.players:
            player.outcome = results[player.id].note
            player.finished = results[player.id].turn_finished

            if not command.game.round_finished:
                continue

            if results[player.id].type == RollResultType.WINNER:
                player.win_counter += 1
            elif results[player.id].type == RollResultType.LOSER:
                player.win_counter = 0
            
        return command.game
        