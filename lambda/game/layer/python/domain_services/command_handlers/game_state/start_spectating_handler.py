

from dataclasses import dataclass

from domain_models import GameAction, Spectator
from domain_models.commands import FinishRoundCommand, NotifyGameStateCommand, StartSpectatingCommand

from ...interfaces import IGameStore, IMediator, ISessionStore, ITransactionWriter


@dataclass
class StartSpectatingHandler:
    game_store: IGameStore
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: StartSpectatingCommand):

        session = self.session_store.get(command.session_id)

        game = self.game_store.get(session.game_id)

        matching_players = [p for p in game.players if p.id == session.id]
        if not matching_players:
            return game

        player = matching_players[0]

        game.modified_action = GameAction.START_SPECTATING
        game.modified_by = session.id
        game.players.remove(player)
        game.spectators.append(Spectator(
            id=player.id,
            account_id=player.account_id,
            nickname=player.nickname
        ))

        is_round_now_finished = all([p.finished for p in game.players])
        if not game.round_finished and is_round_now_finished:
            game = self.mediator.send(FinishRoundCommand(game))

        with self.transaction_writer.create() as transaction:
            self.game_store.set(game, transaction)

        self.mediator.send(NotifyGameStateCommand(game))
