
from dataclasses import dataclass

from domain_models.commands import CreateSessionCommand, CreateSessionIdCommand, NotifyConnectionsCommand

from ...interfaces import IMediator, ITransactionWriter, IWebsocketConnectionStore
from ...transaction_utils import concurrency_retry


@dataclass
class CreateSessionIdHandler:
    mediator: IMediator
    transaction_writer: ITransactionWriter
    websocket_connection_store: IWebsocketConnectionStore

    def handle(self, command: CreateSessionIdCommand) -> str:
        return self._create_session_id(command)

    @concurrency_retry
    def _create_session_id(self, command: CreateSessionIdCommand) -> str:

        connection = self.websocket_connection_store.get(command.connection_id)

        with self.transaction_writer.create() as transaction:
            session_id = self.mediator.send(CreateSessionCommand(command.connection_id, transaction))

            connection.session_id = session_id

            self.websocket_connection_store.set(connection, transaction)

        self.mediator.send(NotifyConnectionsCommand(
            connection_ids=[connection.connection_id],
            action='getSession',
            data=connection.session_id
        ))

        return session_id
