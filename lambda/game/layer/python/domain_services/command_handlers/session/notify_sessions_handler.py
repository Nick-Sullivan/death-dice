

from dataclasses import dataclass

from domain_models.commands import NotifyConnectionsCommand, NotifySessionsCommand

from ...interfaces import IMediator, ISessionStore


@dataclass
class NotifySessionsHandler:
    mediator: IMediator
    session_store: ISessionStore

    def handle(self, command: NotifySessionsCommand):
        connection_ids = []
        for session_id in command.session_ids:
            session = self.session_store.get(session_id)
            connection_ids.append(session.connection_id)

        self.mediator.send(NotifyConnectionsCommand(connection_ids, command.action, command.data, command.error))
