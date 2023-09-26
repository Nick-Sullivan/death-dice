
from dataclasses import dataclass

from domain_models import SessionAction
from domain_models.commands import CheckSessionTimeoutCommand, DestroySessionCommand

from ...interfaces import IMediator, ISessionStore, ITransactionWriter, SessionNotFoundException
from ...transaction_utils import concurrency_retry


@dataclass
class CheckSessionTimeoutHandler:
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: CheckSessionTimeoutCommand) -> str:
        return self.check_session_timeout(command)

    @concurrency_retry
    def check_session_timeout(self, command: CheckSessionTimeoutCommand):
        try:
            session = self.session_store.get(command.session_id)
        except SessionNotFoundException:
            return

        if session.modified_action != SessionAction.PENDING_TIMEOUT:
            return

        self.mediator.send(DestroySessionCommand(command.session_id))
