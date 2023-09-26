

from dataclasses import dataclass

from domain_models import WebsocketConnectionItem
from domain_models.commands import MarkSessionAsConnectedCommand, NotifyConnectionsCommand, SetSessionIdCommand

from ...interfaces import IMediator, ITransactionWriter, IWebsocketConnectionStore, SessionNotFoundException
from ...transaction_utils import concurrency_retry


@dataclass
class SetSessionIdHandler:
    mediator: IMediator
    transaction_writer: ITransactionWriter
    websocket_connection_store: IWebsocketConnectionStore

    def handle(self, command: SetSessionIdCommand):
        self._set_session_id(command)

    @concurrency_retry
    def _set_session_id(self, command: SetSessionIdCommand):
        connection = self.websocket_connection_store.get(command.connection_id)
        connection.session_id = command.session_id

        with self.transaction_writer.create() as transaction:
            
            transaction.then(lambda: self._send_successful_session_message(connection))

            try:
                self.mediator.send(MarkSessionAsConnectedCommand(
                    connection_id=command.connection_id,
                    session_id=command.session_id,
                    transaction=transaction
                ))
            except SessionNotFoundException:
                self._send_invalid_session_message(command.connection_id)
                transaction.clear()
                return

            self.websocket_connection_store.set(connection, transaction)
        

    def _send_invalid_session_message(self, connection_id: str):
        self.mediator.send(NotifyConnectionsCommand(
            connection_ids=[connection_id],
            action='setSession',
            error='Invalid session ID'
        ))

    def _send_successful_session_message(self, connection: WebsocketConnectionItem):
        self.mediator.send(NotifyConnectionsCommand(
            connection_ids=[connection.connection_id],
            action='getSession',
            data=connection.session_id
        ))
    