
from dataclasses import dataclass

from domain_models import WebsocketConnectionItem
from domain_models.commands import CreateConnectionCommand

from ...interfaces import ITransactionWriter, IWebsocketConnectionStore


@dataclass
class CreateConnectionHandler:
    transaction_writer: ITransactionWriter
    websocket_connection_store: IWebsocketConnectionStore

    def handle(self, command: CreateConnectionCommand) -> WebsocketConnectionItem:
        connection = WebsocketConnectionItem(
            connection_id=command.connection_id,
            session_id=None,
        )

        with self.transaction_writer.create() as transaction:
            self.websocket_connection_store.create(connection, transaction)
        return connection
    