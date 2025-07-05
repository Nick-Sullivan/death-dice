
from dataclasses import dataclass

from domain_models import SessionAction
from domain_models.commands import MarkPlayerAsConnectedCommand, MarkSessionAsConnectedCommand

from ...interfaces import IMediator, ISessionStore


@dataclass
class MarkSessionAsConnectedHandler:
    mediator: IMediator
    session_store: ISessionStore

    def handle(self, command: MarkSessionAsConnectedCommand):
        session = self.session_store.get(command.session_id)
        session.modified_action = SessionAction.RECONNECTED
        session.connection_id = command.connection_id
        self.session_store.set(session, command.transaction)

        if session.game_id:
            self.mediator.send(MarkPlayerAsConnectedCommand(
                command.session_id,
                session.game_id,
                transaction=command.transaction
            ))
