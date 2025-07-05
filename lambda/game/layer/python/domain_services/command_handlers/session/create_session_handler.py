
import uuid
from dataclasses import dataclass

from domain_models import SessionAction, SessionItem
from domain_models.commands import CreateSessionCommand

from ...interfaces import ISessionStore


@dataclass
class CreateSessionHandler:
    session_store: ISessionStore

    def handle(self, command: CreateSessionCommand) -> str:

        session_id = self.create_session_id()

        session = SessionItem(
            id=session_id,
            connection_id=command.connection_id,
            modified_action=SessionAction.CREATE_CONNECTION,
        )

        self.session_store.create(session, command.transaction)

        return session_id


    def create_session_id(self) -> str:
        return str(uuid.uuid4())
