
from dataclasses import dataclass

from domain_models import ConnectionStatus, GameAction, GameState, Player, RollResultNote, SessionAction
from domain_models.commands import CreateGameCommand, NotifyConnectionsCommand, NotifyGameStateCommand
from domain_services.transaction_utils import concurrency_retry

from ...interfaces import IEventPublisher, IGameStore, IMediator, ISessionStore, ITransactionWriter


@dataclass
class CreateGameHandler:
    event_publisher: IEventPublisher
    game_store: IGameStore
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: CreateGameCommand):
        return self._create_game(command)
    
    @concurrency_retry
    def _create_game(self, command: CreateGameCommand) -> GameState:
        game_id = self.game_store.create_unique_game_id()

        session = self.session_store.get(command.session_id)
        session.game_id = game_id
        session.modified_action = SessionAction.JOIN_GAME

        game = GameState(
            id=game_id,
            mr_eleven='',
            round_id=0,
            round_finished=True,
            players=[Player(
                id=session.id,
                account_id=session.account_id,
                nickname=session.nickname,
                win_counter=0,
                finished=False,
                outcome=RollResultNote.NONE,
                rolls=[],
                connection_status=ConnectionStatus.CONNECTED,
            )],
            spectators=[],
            modified_action=GameAction.CREATE_GAME,
            modified_by=session.id,
        )

        with self.transaction_writer.create() as transaction:
            self.game_store.create(game, transaction)
            self.session_store.set(session, transaction)

        self.mediator.send(NotifyConnectionsCommand(
            [session.connection_id],
            action='joinGame',
            data=game.id,
        ))

        self.mediator.send(NotifyGameStateCommand(game))

        self._publish_new_game_event(game.id)

        return game

    def _publish_new_game_event(self, game_id: str):
        self.event_publisher.publish_event(
            source='GameCreated',
            detail_type='Game created',
            detail={'game_id': game_id}
        )
