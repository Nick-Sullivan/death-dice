
from dataclasses import dataclass

from domain_models import GameAction, GameState
from domain_models.commands import FinishRoundCommand, LeaveGameCommand, NotifyGameStateCommand

from ...interfaces import IGameStore, IMediator


@dataclass
class LeaveGameHandler:
    game_store: IGameStore
    mediator: IMediator

    def handle(self, command: LeaveGameCommand):

        game = self.game_store.get(command.game_id)
        game.modified_action = GameAction.LEAVE_GAME
        game.modified_by = command.session_id

        if self._is_last_connection(game):
            self.game_store.delete(game, command.transaction)
            return None

        if self._is_spectator(command.session_id, game):
            game.spectators = [
                s for s in game.spectators
                if s.id != command.session_id
            ]
        else:
            game.players = [
                p for p in game.players
                if p.id != command.session_id
            ]
            if self._is_round_finished(game):
                game = self.mediator.send(FinishRoundCommand(game))

        self.game_store.set(game, command.transaction)

        command.transaction.then(lambda: self.mediator.send(NotifyGameStateCommand(game)))
        
    @staticmethod
    def _is_last_connection(game: GameState):
        return len(game.players) + len(game.spectators) <= 1

    @staticmethod
    def _is_spectator(session_id: str, game: GameState):
        return any(s for s in game.spectators if s.id == session_id)

    @staticmethod
    def _is_round_finished(game: GameState):
        return all([p.finished for p in game.players])