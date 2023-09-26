

from dataclasses import dataclass

from domain_models.commands import GetSessionIdCommand, NotifyConnectionsCommand

from ...interfaces import IMediator, IWebsocketConnectionStore


@dataclass
class GetSessionIdHandler:
    mediator: IMediator
    websocket_connection_store: IWebsocketConnectionStore

    def handle(self, command: GetSessionIdCommand) -> str:

        connection = self.websocket_connection_store.get(command.connection_id)
        
        if connection.session_id:
            self.mediator.send(NotifyConnectionsCommand(
                connection_ids=[connection.connection_id],
                action='getSession',
                data=connection.session_id
            ))
            
        return connection.session_id
