
from dataclasses import dataclass

from domain_models.commands import DestroyConnectionCommand, MarkSessionAsPendingCommand

from ...interfaces import IEventPublisher, IMediator, ITransactionWriter, IWebsocketConnectionStore
from ...transaction_utils import concurrency_retry


@dataclass
class DestroyConnectionHandler:
    event_publisher: IEventPublisher
    mediator: IMediator
    transaction_writer: ITransactionWriter
    websocket_connection_store: IWebsocketConnectionStore

    def handle(self, command: DestroyConnectionCommand):
        self.destroy_connection(command)

    @concurrency_retry
    def destroy_connection(self, command: DestroyConnectionCommand):
        connection = self.websocket_connection_store.get(command.connection_id)

        with self.transaction_writer.create() as transaction:
            self.websocket_connection_store.delete(connection, transaction)

            if connection.session_id:
                self.mediator.send(MarkSessionAsPendingCommand(
                    session_id=connection.session_id,
                    transaction=transaction,
                ))
                
        if connection.session_id:
            self.event_publisher.publish_event(
                source='Websocket',
                detail_type='Disconnected',
                detail={
                    'connection_id': command.connection_id,
                    'session_id': connection.session_id,
                }
            )
