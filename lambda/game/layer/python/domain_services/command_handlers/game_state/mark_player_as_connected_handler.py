
from dataclasses import dataclass

from domain_models import ConnectionStatus
from domain_models.commands import MarkPlayerAsConnectedCommand, NotifyGameStateCommand

from ...interfaces import IGameStore, IMediator


@dataclass
class MarkPlayerAsConnectedHandler:
    game_store: IGameStore
    mediator: IMediator

    def handle(self, command: MarkPlayerAsConnectedCommand):

        game = self.game_store.get(command.game_id)

        player = next(p for p in game.players+game.spectators if p.id == command.session_id)
        player.connection_status = ConnectionStatus.CONNECTED

        self.game_store.set(game, command.transaction)

        command.transaction.then(lambda: self.mediator.send(NotifyGameStateCommand(game)))
