
from dataclasses import dataclass

from domain_models import SessionAction
from domain_models.commands import MarkPlayerAsPendingCommand, MarkSessionAsPendingCommand

from ...interfaces import IMediator, ISessionStore


@dataclass
class MarkSessionAsPendingHandler:
    mediator: IMediator
    session_store: ISessionStore

    def handle(self, command: MarkSessionAsPendingCommand):
        session = self.session_store.get(command.session_id)
        session.modified_action = SessionAction.PENDING_TIMEOUT
        self.session_store.set(session, command.transaction)

        if session.game_id:
            self.mediator.send(MarkPlayerAsPendingCommand(
                command.session_id,
                session.game_id,
                transaction=command.transaction,
            ))
