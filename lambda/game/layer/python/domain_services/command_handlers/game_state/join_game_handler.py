

from dataclasses import dataclass

from domain_models import ConnectionStatus, GameAction, Player, RollResultNote, SessionAction
from domain_models.commands import JoinGameCommand, NotifyConnectionsCommand, NotifyGameStateCommand
from domain_services.interfaces import GameNotFoundException, IGameStore, ISessionStore, ITransactionWriter
from domain_services.transaction_utils import concurrency_retry

from ...interfaces import IMediator


@dataclass
class JoinGameHandler:
    game_store: IGameStore
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: JoinGameCommand) -> str:
       return self.join_game(command)
    
    @concurrency_retry
    def join_game(self, command: JoinGameCommand):
        
        session = self.session_store.get(command.session_id)

        try:
            game = self.game_store.get(command.game_id)

        except GameNotFoundException:
            self.mediator.send(NotifyConnectionsCommand(
                [session.connection_id],
                action='joinGame',
                error=f'Unable to join game: {command.game_id}'
            ))
            return

        game.modified_action = GameAction.JOIN_GAME
        game.modified_by = session.id
        
        session.game_id = game.id
        session.modified_action = SessionAction.JOIN_GAME
        
        game.players.append(Player(
            id=session.id,
            account_id=session.account_id,
            nickname=session.nickname,
            win_counter=0,
            finished=False,
            outcome=RollResultNote.NONE,
            rolls=[],
            connection_status=ConnectionStatus.CONNECTED,
        ))

        with self.transaction_writer.create() as transaction:
            self.game_store.set(game, transaction)
            self.session_store.set(session, transaction)

        self.mediator.send(NotifyConnectionsCommand(
            [session.connection_id],
            action='joinGame',
            data=game.id
        ))

        self.mediator.send(NotifyGameStateCommand(game))

        return game
