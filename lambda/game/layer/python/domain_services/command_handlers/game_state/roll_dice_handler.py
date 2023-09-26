

from dataclasses import dataclass

from domain_models import GameAction
from domain_models.commands import (
    CalculateIndividualResultCommand,
    DecideDiceValuesCommand,
    FinishRoundCommand,
    NotifyGameStateCommand,
    RollDiceCommand,
)

from ...interfaces import IGameStore, IMediator, ISessionStore, ITransactionWriter
from ...transaction_utils import concurrency_retry


@dataclass
class RollDiceHandler:
    game_store: IGameStore
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: RollDiceCommand):
        return self.roll_dice(command)
    
    @concurrency_retry
    def roll_dice(self, command: RollDiceCommand):
        
        session = self.session_store.get(command.session_id)

        game = self.game_store.get(session.game_id)

        player = next(p for p in game.players if p.id == session.id)

        if player.finished:
            return game

        game.modified_action = GameAction.ROLL_DICE
        game.modified_by = session.id

        new_roll = self.mediator.send(DecideDiceValuesCommand(player.rolls, player.win_counter, player.nickname))
        player.rolls.append(new_roll)

        roll_result = self.mediator.send(CalculateIndividualResultCommand(player.rolls, player.nickname == game.mr_eleven))

        player.finished = roll_result.turn_finished
        player.outcome = roll_result.note

        is_round_finished = all([p.finished for p in game.players])
        if is_round_finished:
            game = self.mediator.send(FinishRoundCommand(game))
        
        with self.transaction_writer.create() as transaction:
            self.game_store.set(game, transaction)
            
        self.mediator.send(NotifyGameStateCommand(game))
