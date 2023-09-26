
from dataclasses import dataclass

from domain_models import ConnectionStatus, GameAction, Player, RollResultNote
from domain_models.commands import NotifyGameStateCommand, StopSpectatingCommand

from ...interfaces import IGameStore, IMediator, ISessionStore, ITransactionWriter


@dataclass
class StopSpectatingHandler:
    game_store: IGameStore
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: StopSpectatingCommand):

        session = self.session_store.get(command.session_id)

        game = self.game_store.get(session.game_id)

        matching_spectators = [s for s in game.spectators if s.id == session.id]
        if not matching_spectators:
            return game

        spectator = matching_spectators[0]

        game.modified_action = GameAction.STOP_SPECTATING
        game.modified_by = session.id
        game.spectators.remove(spectator)
        game.players.append(Player(
            id=spectator.id,
            account_id=spectator.account_id,
            nickname=spectator.nickname,
            win_counter=0,
            finished=False,
            outcome=RollResultNote.NONE,
            rolls=[],
            connection_status=ConnectionStatus.CONNECTED
        ))

        with self.transaction_writer.create() as transaction:
            self.game_store.set(game, transaction)

        self.mediator.send(NotifyGameStateCommand(game))
