

from dataclasses import dataclass

from domain_models import GameAction, RollResultNote
from domain_models.commands import NewRoundCommand, NotifyGameStateCommand

from ...interfaces import IGameStore, IMediator, ISessionStore, ITransactionWriter
from ...transaction_utils import concurrency_retry


@dataclass
class NewRoundHandler:
    game_store: IGameStore
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: NewRoundCommand) -> str:
       return self.new_round(command)

    @concurrency_retry
    def new_round(self, command: NewRoundCommand):
        
        session = self.session_store.get(command.session_id)
            
        game = self.game_store.get(session.game_id)

        if not game.round_finished:
            return game

        game.round_id += 1
        game.round_finished = False
        game.modified_action = GameAction.NEW_ROUND
        game.modified_by = session.id

        for player in game.players:
            player.outcome = RollResultNote.NONE
            player.finished = False
            player.rolls = []
            
        with self.transaction_writer.create() as transaction:
            self.game_store.set(game, transaction)
            
        self.mediator.send(NotifyGameStateCommand(game))
