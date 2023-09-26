
from dataclasses import dataclass

from domain_models.commands import DestroySessionCommand, LeaveGameCommand, NotifyConnectionsCommand

from ...interfaces import IMediator, ISessionStore, ITransactionWriter
from ...transaction_utils import concurrency_retry


@dataclass
class DestroySessionHandler:
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: DestroySessionCommand):
        return self.destroy_session(command)

    @concurrency_retry
    def destroy_session(self, command: DestroySessionCommand):

        with self.transaction_writer.create() as transaction:

            session = self.session_store.get(command.session_id)
            
            self.session_store.delete(session, transaction)

            if session.game_id:
                self.mediator.send(LeaveGameCommand(command.session_id, session.game_id, transaction))

        self.mediator.send(NotifyConnectionsCommand(
            connection_ids=[session.connection_id],
            action='destroySession',
            data=session.id
        ))
